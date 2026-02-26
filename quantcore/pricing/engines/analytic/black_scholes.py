import numpy as np
from scipy.stats import norm
from quantcore.core.base.abc.pricer import PricingEngine
from quantcore.core.base.types.enums import OptionType
from quantcore.instruments.derivatives.options.european import EuropeanOption
from typing import Dict, Any

class BlackScholesEngine(PricingEngine):
    """
    Analytic pricing engine for European Options using Black-Scholes-Merton.
    """
    
    def __init__(self):
        self._results = {}

    def calculate(self, instrument: EuropeanOption) -> float:
        if not isinstance(instrument, EuropeanOption):
            raise TypeError("Engine only supports EuropeanOptions")
            
        S = instrument.underlying_price
        K = instrument.strike_price
        T = instrument.time_to_maturity
        r = instrument.risk_free_rate
        sigma = instrument.volatility
        q = instrument.dividend_yield
        
        if T <= 0:
            val = instrument.payoff(S)
            self._results['npv'] = val
            return val
            
        d1 = (np.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if instrument.option_type == OptionType.CALL:
            price = S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        else:
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)
            
        # Store metadata/greeks inside results
        self._results = {
            'npv': float(price),
            'd1': float(d1),
            'd2': float(d2)
        }
        return float(price)

    def get_results(self) -> Dict[str, Any]:
        return self._results

    @classmethod
    def can_price(cls, instrument: Any) -> bool:
        return isinstance(instrument, EuropeanOption)
