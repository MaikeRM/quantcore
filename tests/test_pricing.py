import pytest
import numpy as np
from quantcore.instruments.derivatives.options.european import EuropeanOption
from quantcore.core.base.types.enums import OptionType
from quantcore.pricing.engines import PricingEngineFactory, EngineType

def test_black_scholes_call():
    # Setup option based on standard textbook example
    opt = EuropeanOption(
        underlying_price=100.0,
        strike_price=100.0,
        time_to_maturity=1.0,
        risk_free_rate=0.05,
        volatility=0.2,
        dividend_yield=0.0,
        option_type=OptionType.CALL
    )
    
    factory = PricingEngineFactory()
    engine = factory.create_engine(opt, EngineType.ANALYTIC)
    
    price = engine.calculate(opt)
    
    # BSM call price for ATM S=100, K=100, T=1, r=0.05, v=0.2 is approx 10.4506
    assert np.isclose(price, 10.45058, atol=1e-4)

def test_black_scholes_put():
    opt = EuropeanOption(
        underlying_price=100.0,
        strike_price=100.0,
        time_to_maturity=1.0,
        risk_free_rate=0.05,
        volatility=0.2,
        dividend_yield=0.0,
        option_type=OptionType.PUT
    )
    
    factory = PricingEngineFactory()
    engine = factory.create_engine(opt, EngineType.ANALYTIC)
    
    price = engine.calculate(opt)
    
    # Put-Call Parity: P = C - S + K*e^(-r*T)
    # P = 10.45058 - 100 + 100*exp(-0.05) = 10.45058 - 100 + 95.1229 = 5.5735
    assert np.isclose(price, 5.5735, atol=1e-4)

def test_expired_option():
    opt = EuropeanOption(
        underlying_price=105.0,
        strike_price=100.0,
        time_to_maturity=0.0,
        risk_free_rate=0.0,
        volatility=0.0,
        option_type=OptionType.CALL
    )
    
    factory = PricingEngineFactory()
    engine = factory.create_engine(opt, EngineType.ANALYTIC)
    price = engine.calculate(opt)
    
    assert price == 5.0 # Intrinsic value since expired
