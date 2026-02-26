from abc import ABC, abstractmethod
from typing import Dict, Any
import numpy as np

class StochasticModel(ABC):
    """
    Abstract base class for all stochastic models (e.g., Black-Scholes, Heston).
    """

    @property
    @abstractmethod
    def default_parameters(self) -> Dict[str, float]:
        """Return the default parameters of the model."""
        pass

    @abstractmethod
    def simulate_paths(self, n_paths: int, n_steps: int, T: float, seed: int = None) -> np.ndarray:
        """
        Simulate asset paths.
        
        Returns
        -------
        np.ndarray
            Array of shape (n_paths, n_steps + 1)
        """
        pass
