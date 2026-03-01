"""
Integration test — end-to-end flow.

Simulates a real-world workflow:
  Instrument → YieldCurve → PricingEngine → Pricing → Risk (VaR)

This is the "grand test" that proves all modules work together.
"""

import pytest
import numpy as np

from quantcore.core.time.date import Date
from quantcore.core.time.daycount import Actual365
from quantcore.core.base.types.enums import OptionType
from quantcore.instruments.derivatives.options.european import EuropeanOption
from quantcore.instruments.fixed_income.bonds.fixed_rate import FixedRateBond
from quantcore.market.curves import YieldCurve, YieldCurveBuilder
from quantcore.pricing.engines import PricingEngineFactory, EngineType
from quantcore.pricing.engines.analytic.black_scholes import BlackScholesEngine
from quantcore.risk.metrics.market_risk.value_at_risk import ValueAtRisk
from quantcore.core.math.calculus.differentiation import FiniteDifference
from quantcore.core.math.statistics.distributions.student_t import StudentTDistribution


class TestIntegrationEndToEnd:
    """
    End-to-end integration test:
    Build a yield curve → create instruments → price them → compute risk.
    """

    @pytest.fixture
    def yield_curve(self):
        """Bootstrap a realistic yield curve."""
        instruments = [
            ("deposit", 0.25, 0.02),
            ("deposit", 0.5, 0.025),
            ("swap", 1.0, 0.03),
            ("swap", 2.0, 0.035),
            ("swap", 5.0, 0.04),
            ("swap", 10.0, 0.045),
        ]
        builder = YieldCurveBuilder()
        return builder.bootstrap(instruments)

    @pytest.fixture
    def european_call(self, yield_curve):
        """European call option using the yield curve rate as risk-free rate."""
        r = yield_curve.zero_rate(1.0)  # 1-year rate
        return EuropeanOption(
            underlying_price=100.0,
            strike_price=105.0,
            time_to_maturity=1.0,
            risk_free_rate=r,
            volatility=0.25,
            option_type=OptionType.CALL,
        )

    @pytest.fixture
    def european_put(self, yield_curve):
        r = yield_curve.zero_rate(1.0)
        return EuropeanOption(
            underlying_price=100.0,
            strike_price=105.0,
            time_to_maturity=1.0,
            risk_free_rate=r,
            volatility=0.25,
            option_type=OptionType.PUT,
        )

    # ── Flow 1: Instrument → Factory → Engine → Price ────────────────

    def test_option_pricing_via_factory(self, european_call):
        """Full pipeline: create engine via factory, price the option."""
        factory = PricingEngineFactory()
        engine = factory.create_engine(european_call, EngineType.ANALYTIC)

        price = engine.calculate(european_call)

        assert price > 0, "Option price must be positive"
        assert price < european_call.underlying_price, "Call price < spot"

        # Check results are populated
        results = engine.get_results()
        assert "npv" in results
        assert "d1" in results
        assert "d2" in results

    # ── Flow 2: Put-Call Parity check ─────────────────────────────────

    def test_put_call_parity(self, european_call, european_put):
        """C - P = S·e^(-qT) - K·e^(-rT) (put-call parity)."""
        factory = PricingEngineFactory()

        engine_call = factory.create_engine(european_call, EngineType.ANALYTIC)
        engine_put = factory.create_engine(european_put, EngineType.ANALYTIC)

        call_price = engine_call.calculate(european_call)
        put_price = engine_put.calculate(european_put)

        S = european_call.underlying_price
        K = european_call.strike_price
        r = european_call.risk_free_rate
        T = european_call.time_to_maturity
        q = european_call.dividend_yield

        # Put-Call Parity: C - P = S*e^(-qT) - K*e^(-rT)
        lhs = call_price - put_price
        rhs = S * np.exp(-q * T) - K * np.exp(-r * T)

        assert pytest.approx(lhs, abs=1e-6) == rhs

    # ── Flow 3: Numerical Greeks via FiniteDifference ─────────────────

    def test_numerical_delta(self, european_call):
        """Compute delta numerically: dC/dS using finite differences."""
        factory = PricingEngineFactory()
        engine = factory.create_engine(european_call, EngineType.ANALYTIC)

        def price_func(S):
            opt = EuropeanOption(
                underlying_price=S,
                strike_price=european_call.strike_price,
                time_to_maturity=european_call.time_to_maturity,
                risk_free_rate=european_call.risk_free_rate,
                volatility=european_call.volatility,
                option_type=european_call.option_type,
            )
            return engine.calculate(opt)

        delta = FiniteDifference.gradient_1d(
            price_func, european_call.underlying_price
        )

        # Delta of a call should be between 0 and 1
        assert 0 < delta < 1

    def test_numerical_gamma(self, european_call):
        """Compute gamma numerically: d²C/dS² using finite differences."""
        factory = PricingEngineFactory()
        engine = factory.create_engine(european_call, EngineType.ANALYTIC)

        def price_func(S):
            opt = EuropeanOption(
                underlying_price=S,
                strike_price=european_call.strike_price,
                time_to_maturity=european_call.time_to_maturity,
                risk_free_rate=european_call.risk_free_rate,
                volatility=european_call.volatility,
                option_type=european_call.option_type,
            )
            return engine.calculate(opt)

        gamma = FiniteDifference.hessian_1d(
            price_func, european_call.underlying_price
        )

        # Gamma is always positive for vanilla options
        assert gamma > 0

    # ── Flow 4: YieldCurve → Discount Factors → DayCount ─────────────

    def test_curve_daycount_integration(self, yield_curve):
        """Combine yield curve with day counter."""
        dc = Actual365()
        d1 = Date(2024, 1, 1)
        d2 = Date(2025, 1, 1)

        T = dc.year_fraction(d1, d2)
        assert T > 0

        df = yield_curve.discount_factor(T)
        assert 0 < df < 1

        r = yield_curve.zero_rate(T)
        assert r > 0

        # Consistency: DF = exp(-r*T)
        assert pytest.approx(df, abs=1e-6) == np.exp(-r * T)

    # ── Flow 5: Return Simulation → VaR → Distribution Fit ───────────

    def test_risk_var_with_distribution(self, rng):
        """Simulate returns, fit t-dist, compute VaR with both methods."""
        # Simulate returns
        returns = rng.normal(0.0005, 0.02, 1000)

        # VaR via historical
        var_calc = ValueAtRisk(confidence_level=0.95, horizon=1)
        h_var = var_calc.historical(returns)
        p_var = var_calc.parametric_normal(returns)

        assert h_var > 0
        assert p_var > 0

        # Fit t-distribution
        fitted = StudentTDistribution.fit(returns, method="mle")
        assert fitted.df > 0
        assert fitted.scale > 0

        # Distribution VaR
        dist_var = fitted.var(0.05)
        # Should be negative (loss in left tail)
        assert dist_var < 0

    # ── Flow 6: Multiple Instruments Pricing ──────────────────────────

    def test_portfolio_pricing(self, yield_curve):
        """Price a portfolio of options with different strikes."""
        r = yield_curve.zero_rate(0.5)
        factory = PricingEngineFactory()

        strikes = [90.0, 95.0, 100.0, 105.0, 110.0]
        prices = []

        for K in strikes:
            opt = EuropeanOption(
                underlying_price=100.0,
                strike_price=K,
                time_to_maturity=0.5,
                risk_free_rate=r,
                volatility=0.20,
                option_type=OptionType.CALL,
            )
            engine = factory.create_engine(opt)
            price = engine.calculate(opt)
            prices.append(price)

        # Call prices should decrease as strike increases
        for i in range(len(prices) - 1):
            assert prices[i] > prices[i + 1], (
                f"Call price for K={strikes[i]} should be > K={strikes[i+1]}"
            )

        # Deep ITM should be close to S - K*e^(-rT)
        deep_itm_price = prices[0]
        intrinsic_pv = 100.0 - 90.0 * np.exp(-r * 0.5)
        assert deep_itm_price >= intrinsic_pv * 0.99  # at least near intrinsic

    # ── Flow 7: Black-Scholes can_price check ─────────────────────────

    def test_engine_can_price_check(self, european_call):
        """BlackScholesEngine.can_price should return True for European options."""
        assert BlackScholesEngine.can_price(european_call) is True

    def test_engine_cannot_price_bond(self):
        bond = FixedRateBond(
            face_value=1000.0,
            coupon_rate=0.05,
            maturity_date=Date(2030, 1, 1),
            frequency=2,
        )
        assert BlackScholesEngine.can_price(bond) is False

    # ── Flow 8: Option metadata round-trip ────────────────────────────

    def test_instrument_metadata_round_trip(self, european_call):
        """Metadata should accurately reflect construction parameters."""
        meta = european_call.get_metadata()
        assert meta["S"] == 100.0
        assert meta["K"] == 105.0
        assert meta["T"] == 1.0
        assert meta["sigma"] == 0.25
        assert "European Call Option" in meta["type"]

    # ── Flow 9: Expired option edge case ──────────────────────────────

    def test_expired_option_returns_intrinsic_value(self):
        """An expired ITM option should return intrinsic value."""
        opt = EuropeanOption(
            underlying_price=110.0,
            strike_price=100.0,
            time_to_maturity=0.0,
            risk_free_rate=0.0,
            volatility=0.0,
            option_type=OptionType.CALL,
        )
        factory = PricingEngineFactory()
        engine = factory.create_engine(opt)
        price = engine.calculate(opt)
        assert price == 10.0

    def test_expired_otm_option_returns_zero(self):
        """An expired OTM option should return 0."""
        opt = EuropeanOption(
            underlying_price=90.0,
            strike_price=100.0,
            time_to_maturity=0.0,
            risk_free_rate=0.0,
            volatility=0.0,
            option_type=OptionType.CALL,
        )
        factory = PricingEngineFactory()
        engine = factory.create_engine(opt)
        price = engine.calculate(opt)
        assert price == 0.0
