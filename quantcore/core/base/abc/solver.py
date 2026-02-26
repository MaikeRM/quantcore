from abc import ABC, abstractmethod
from typing import Callable, Any

class NumericalSolver(ABC):
    """
    Abstract base class for numerical optimizers and solvers.
    """

    @abstractmethod
    def solve(self, objective_function: Callable, initial_guess: Any, **kwargs) -> Any:
        """
        Execute the numerical optimization/solving routine.
        """
        pass
