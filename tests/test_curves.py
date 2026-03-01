"""
Tests for quantcore.market.curves module.

Covers:
  - YieldCurve: construction, zero_rate, forward_rate, discount_factor, 
    flat extrapolation, edge cases
  - YieldCurveBuilder: bootstrap from market instruments
"""

import pytest
import numpy as np
from quantcore.market.curves import YieldCurve, YieldCurveBuilder


# ═══════════════════════════════════════════════════════════════════════
# YieldCurve tests
# ═══════════════════════════════════════════════════════════════════════

class TestYieldCurve:
    """Tests for quantcore.market.curves.yield_.yield_curve.YieldCurve."""

    @pytest.fixture
    def flat_curve(self):
        """A flat yield curve at 5%."""
        times = np.array([0.5, 1.0, 2.0, 5.0, 10.0])
        rates = np.array([0.05, 0.05, 0.05, 0.05, 0.05])
        return YieldCurve(times, rates)

    @pytest.fixture
    def upward_curve(self):
        """A typical upward-sloping yield curve."""
        times = np.array([0.25, 0.5, 1.0, 2.0, 5.0, 10.0])
        rates = np.array([0.02, 0.025, 0.03, 0.035, 0.04, 0.045])
        return YieldCurve(times, rates)

    # ── Construction ──────────────────────────────────────────────────

    def test_construction_valid(self):
        times = np.array([1.0, 2.0])
        rates = np.array([0.05, 0.06])
        curve = YieldCurve(times, rates)
        assert curve.times is not None
        assert curve.rates is not None

    def test_construction_mismatched_lengths_raises(self):
        with pytest.raises(ValueError, match="same length"):
            YieldCurve(np.array([1.0, 2.0]), np.array([0.05]))

    def test_reference_date_none_by_default(self):
        curve = YieldCurve(np.array([1.0, 2.0]), np.array([0.05, 0.06]))
        assert curve.reference_date is None

    def test_reference_date_set(self):
        curve = YieldCurve(np.array([1.0, 2.0]), np.array([0.05, 0.06]), reference_date="2024-01-01")
        assert curve.reference_date == "2024-01-01"

    # ── zero_rate ─────────────────────────────────────────────────────

    def test_zero_rate_at_node(self, flat_curve):
        """Interpolation at a node should return the exact rate."""
        assert pytest.approx(flat_curve.zero_rate(1.0), abs=1e-10) == 0.05

    def test_zero_rate_interpolation(self, upward_curve):
        """Interpolated rate between nodes should be within bounds."""
        r = upward_curve.zero_rate(1.5)
        assert 0.03 <= r <= 0.035

    def test_zero_rate_flat_extrapolation_left(self, upward_curve):
        """Extrapolation below the first node should return the first rate."""
        r = upward_curve.zero_rate(0.01)
        assert pytest.approx(r, abs=1e-10) == 0.02

    def test_zero_rate_flat_extrapolation_right(self, upward_curve):
        """Extrapolation above the last node should return the last rate."""
        r = upward_curve.zero_rate(20.0)
        assert pytest.approx(r, abs=1e-10) == 0.045

    def test_value_is_alias_for_zero_rate(self, upward_curve):
        """value() should return the same as zero_rate()."""
        t = 3.0
        assert upward_curve.value(t) == upward_curve.zero_rate(t)

    # ── forward_rate ──────────────────────────────────────────────────

    def test_forward_rate_flat_curve(self, flat_curve):
        """Forward rate on a flat curve should equal the zero rate."""
        fwd = flat_curve.forward_rate(1.0, 2.0)
        assert pytest.approx(fwd, abs=1e-6) == 0.05

    def test_forward_rate_upward_curve(self, upward_curve):
        """Forward rate should be higher than the shorter zero rate on upward curve."""
        fwd = upward_curve.forward_rate(1.0, 5.0)
        r1 = upward_curve.zero_rate(1.0)
        assert fwd > r1

    def test_forward_rate_t1_equals_t2_raises(self, flat_curve):
        with pytest.raises(ValueError, match="t2 must be strictly greater"):
            flat_curve.forward_rate(1.0, 1.0)

    def test_forward_rate_t1_greater_than_t2_raises(self, flat_curve):
        with pytest.raises(ValueError, match="t2 must be strictly greater"):
            flat_curve.forward_rate(2.0, 1.0)

    def test_forward_rate_consistency(self, upward_curve):
        """f(t1,t2) = (r2*t2 - r1*t1)/(t2-t1) identity check."""
        t1, t2 = 1.0, 5.0
        r1 = upward_curve.zero_rate(t1)
        r2 = upward_curve.zero_rate(t2)
        expected = (r2 * t2 - r1 * t1) / (t2 - t1)
        actual = upward_curve.forward_rate(t1, t2)
        assert pytest.approx(actual, abs=1e-10) == expected

    # ── discount_factor ───────────────────────────────────────────────

    def test_discount_factor_at_zero(self, flat_curve):
        """DF at time 0 should be 1 (or very close)."""
        df = flat_curve.discount_factor(0.0)
        assert pytest.approx(df, abs=1e-10) == 1.0

    def test_discount_factor_positive_rate(self, flat_curve):
        """DF should be less than 1 for positive rates and positive time."""
        df = flat_curve.discount_factor(1.0)
        assert df < 1.0
        assert pytest.approx(df, abs=1e-6) == np.exp(-0.05 * 1.0)

    def test_discount_factor_increases_duration(self, upward_curve):
        """Longer maturity should have smaller DF."""
        df1 = upward_curve.discount_factor(1.0)
        df5 = upward_curve.discount_factor(5.0)
        assert df5 < df1

    def test_discount_factor_consistency(self, upward_curve):
        """P(0,t) = exp(-r(t)*t) identity check."""
        t = 3.0
        r = upward_curve.zero_rate(t)
        expected = np.exp(-r * t)
        actual = upward_curve.discount_factor(t)
        assert pytest.approx(actual, abs=1e-10) == expected


# ═══════════════════════════════════════════════════════════════════════
# YieldCurveBuilder tests
# ═══════════════════════════════════════════════════════════════════════

class TestYieldCurveBuilder:
    """Tests for the simplistic YieldCurveBuilder.bootstrap."""

    @pytest.fixture
    def builder(self):
        return YieldCurveBuilder()

    def test_bootstrap_returns_yield_curve(self, builder):
        instruments = [
            ("swap", 1.0, 0.03),
            ("swap", 2.0, 0.035),
            ("swap", 5.0, 0.04),
        ]
        curve = builder.bootstrap(instruments)
        assert isinstance(curve, YieldCurve)

    def test_bootstrap_preserves_rates(self, builder):
        instruments = [
            ("bond", 0.5, 0.02),
            ("bond", 1.0, 0.03),
            ("bond", 3.0, 0.04),
        ]
        curve = builder.bootstrap(instruments)
        # At exact nodes, the rate should match the input
        assert pytest.approx(curve.zero_rate(0.5), abs=1e-10) == 0.02
        assert pytest.approx(curve.zero_rate(1.0), abs=1e-10) == 0.03
        assert pytest.approx(curve.zero_rate(3.0), abs=1e-10) == 0.04

    def test_bootstrap_sorts_by_time(self, builder):
        """Instruments given out of order should still produce a valid curve."""
        instruments = [
            ("swap", 5.0, 0.04),
            ("swap", 1.0, 0.03),
            ("swap", 0.25, 0.02),
        ]
        curve = builder.bootstrap(instruments)
        assert curve.times[0] < curve.times[-1]

    def test_bootstrap_curve_is_callable(self, builder):
        instruments = [
            ("swap", 1.0, 0.03),
            ("swap", 5.0, 0.04),
        ]
        curve = builder.bootstrap(instruments)
        # Should be able to query any point
        r = curve.zero_rate(3.0)
        assert 0.03 <= r <= 0.04
