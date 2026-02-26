from typing import Any, Dict
from quantcore.core.base.abc.instrument import FinancialInstrument
from quantcore.core.base.types.enums import OptionType
import numpy as np

class EuropeanOption(FinancialInstrument):
    """
    Standard European Option implementation.
    """
    
    def __init__(self,
                 underlying_price: float,
                 strike_price: float,
                 time_to_maturity: float,
                 risk_free_rate: float,
                 volatility: float,
                 dividend_yield: float = 0.0,
                 option_type: OptionType = OptionType.CALL):
                 
        self.underlying_price = underlying_price
        self.strike_price = strike_price
        self.time_to_maturity = time_to_maturity
        self.risk_free_rate = risk_free_rate
        self.volatility = volatility
        self.dividend_yield = dividend_yield
        self.option_type = option_type
        
    @property
    def instrument_type(self) -> str:
        return f"European {'Call' if self.option_type == OptionType.CALL else 'Put'} Option"

    @property
    def currency(self) -> str:
        # Default fallback currency
        return "USD"
        
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "S": self.underlying_price,
            "K": self.strike_price,
            "T": self.time_to_maturity,
            "r": self.risk_free_rate,
            "sigma": self.volatility,
            "q": self.dividend_yield,
            "type": self.instrument_type
        }
        
    def is_expired(self) -> bool:
        return self.time_to_maturity <= 0.0
        
    def payoff(self, St: float) -> float:
        """Returns the intrinsic value at expiration for a given stock price St."""
        if self.option_type == OptionType.CALL:
            return float(np.maximum(St - self.strike_price, 0.0))
        else:
            return float(np.maximum(self.strike_price - St, 0.0))
