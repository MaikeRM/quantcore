from quantcore.core.base.abc.instrument import FinancialInstrument
from quantcore.core.time.date import Date
from typing import Dict, Any

class BaseBond(FinancialInstrument):
    """Abstract base definition for all bonds."""
    pass
    
class FixedRateBond(BaseBond):
    """
    Vanilla Fixed Rate Bond implementation.
    """
    
    def __init__(self, 
                 face_value: float,
                 coupon_rate: float,
                 maturity_date: Date,
                 frequency: int):
        self.face_value = face_value
        self.coupon_rate = coupon_rate
        self.maturity_date = maturity_date
        self.frequency = frequency
        
    @property
    def instrument_type(self) -> str:
        return "Fixed Rate Bond"
        
    @property
    def currency(self) -> str:
        return "USD"
        
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "Face Value": self.face_value,
            "Coupon Rate": self.coupon_rate,
            "Maturity Date": str(self.maturity_date),
            "Payment Frequency": self.frequency
        }
