from abc import ABC, abstractmethod
from typing import Any, Dict
from .instrument import FinancialInstrument

class PricingEngine(ABC):
    """
    Abstract base class for all pricing engines.
    """

    @abstractmethod
    def calculate(self, instrument: FinancialInstrument) -> float:
        """
        Calculate the value of the instrument.
        """
        pass

    @abstractmethod
    def get_results(self) -> Dict[str, Any]:
        """
        Return auxiliary results generated during pricing.
        """
        pass
