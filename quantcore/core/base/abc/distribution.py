"""
Statistical tools and distributions.
"""
from abc import ABC, abstractmethod
import numpy as np

class ContinuousDistribution(ABC):
    """Base class for continuous statistical distributions."""
    
    @abstractmethod
    def pdf(self, x: np.ndarray) -> np.ndarray:
        pass
        
    @abstractmethod
    def cdf(self, x: np.ndarray) -> np.ndarray:
        pass
        
    @abstractmethod
    def ppf(self, q: np.ndarray) -> np.ndarray:
        pass
