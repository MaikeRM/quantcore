import numpy as np
from typing import Callable
from ...utils.decorators import validate_input

class FiniteDifference:
    """Numerical differentiation strategies."""
    
    @staticmethod
    @validate_input
    def gradient_1d(func: Callable[[float], float], x: float, h: float = 1e-5) -> float:
        """Central difference derivative."""
        return (func(x + h) - func(x - h)) / (2 * h)

    @staticmethod
    @validate_input
    def hessian_1d(func: Callable[[float], float], x: float, h: float = 1e-4) -> float:
        """Second derivative approximation."""
        return (func(x + h) - 2 * func(x) + func(x - h)) / (h ** 2)
