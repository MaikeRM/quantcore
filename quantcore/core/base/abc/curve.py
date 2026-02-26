from abc import ABC, abstractmethod
import numpy as np

class Curve(ABC):
    """
    Abstract base class for financial curves (Yield, Volatility, Survival).
    """

    @property
    @abstractmethod
    def reference_date(self):
        """Return the reference date of the curve."""
        pass

    @abstractmethod
    def value(self, t: float) -> float:
        """
        Get the value at a specific time t.
        """
        pass
