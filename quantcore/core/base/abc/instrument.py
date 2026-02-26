from abc import ABC, abstractmethod
from typing import Any, Dict

class FinancialInstrument(ABC):
    """
    Abstract base class for all financial instruments.
    Every instrument in the library must implement this contract.
    """

    @property
    @abstractmethod
    def instrument_type(self) -> str:
        """Return the type of the instrument."""
        pass

    @property
    @abstractmethod
    def currency(self) -> str:
        """Return the currency of the instrument."""
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Return the instrument's metadata."""
        pass
