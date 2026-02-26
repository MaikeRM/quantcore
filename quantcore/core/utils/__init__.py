"""
Utility modules: decorators, exceptions, logging, and performance helpers.
"""

from .decorators import validate_input, timed
from .exceptions import (
    QuantcoreError,
    ValidationError,
    NumericalError,
    ConvergenceError,
    EngineNotFoundError,
    ConfigurationError,
    DataError,
)
from .logging import get_logger, setup_logging
from .performance import Timer

__all__ = [
    # Decorators
    "validate_input",
    "timed",
    # Exceptions
    "QuantcoreError",
    "ValidationError",
    "NumericalError",
    "ConvergenceError",
    "EngineNotFoundError",
    "ConfigurationError",
    "DataError",
    # Logging
    "get_logger",
    "setup_logging",
    # Performance
    "Timer",
]
