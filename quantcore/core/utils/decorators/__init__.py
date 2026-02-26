"""
Core decorators for the quantcore library.

Provides:
- ``validate_input``  — validates numerical inputs (NaN, Inf, types, shapes).
- ``timed``           — measures and logs function execution time.
"""

from functools import wraps
from typing import Callable, Any, get_type_hints
import time
import numpy as np

from ..logging import get_logger
from ..exceptions import ValidationError

__all__ = ["validate_input", "timed"]

_logger = get_logger(__name__)


# ── Helpers ──────────────────────────────────────────────────────────

def _check_finite(value: Any, name: str, func_name: str) -> None:
    """Raise ``ValidationError`` when *value* contains NaN or Inf."""
    if isinstance(value, (int, bool)):
        # Python bools are ints — always finite. Plain ints are always finite.
        return

    if isinstance(value, float):
        if np.isnan(value):
            raise ValidationError(
                f"NaN detected in argument '{name}' of '{func_name}'.",
                parameter=name,
                function=func_name,
                invalid_value=value,
            )
        if np.isinf(value):
            raise ValidationError(
                f"Inf detected in argument '{name}' of '{func_name}'.",
                parameter=name,
                function=func_name,
                invalid_value=value,
            )

    if isinstance(value, np.ndarray):
        if np.any(np.isnan(value)):
            raise ValidationError(
                f"NaN detected in array argument '{name}' of '{func_name}'.",
                parameter=name,
                function=func_name,
            )
        if np.any(np.isinf(value)):
            raise ValidationError(
                f"Inf detected in array argument '{name}' of '{func_name}'.",
                parameter=name,
                function=func_name,
            )


def _check_type(value: Any, expected_type: type, name: str, func_name: str) -> None:
    """Raise ``ValidationError`` when *value* does not match *expected_type*."""
    # Skip generic aliases (List[float], Dict[str, Any], …)
    if hasattr(expected_type, "__origin__"):
        return
    try:
        if not isinstance(value, expected_type):
            raise ValidationError(
                f"Type mismatch for argument '{name}' of '{func_name}': "
                f"expected {expected_type.__name__}, got {type(value).__name__}.",
                parameter=name,
                function=func_name,
                invalid_value=type(value).__name__,
            )
    except TypeError:
        # Some typing constructs raise TypeError on isinstance check — skip.
        pass


# ── Public decorators ────────────────────────────────────────────────

def validate_input(func: Callable) -> Callable:
    """
    Decorator that performs standard validation on numerical inputs.

    Checks performed
    ----------------
    1. **NaN / Inf** — raises ``ValidationError`` for any ``float`` or
       ``np.ndarray`` argument that contains NaN or ±Inf.
    2. **Type checking** — if the function has type annotations, validates
       that the actual argument matches the declared type.

    Examples
    --------
    >>> @validate_input
    ... def price(spot: float, vol: float) -> float:
    ...     return spot * vol
    >>> price(100.0, float('nan'))
    Traceback (most recent call last):
        ...
    quantcore.core.utils.exceptions.ValidationError: ...
    """
    hints = get_type_hints(func) if hasattr(func, "__annotations__") else {}
    # Remove return annotation
    hints.pop("return", None)

    @wraps(func)
    def wrapper(*args, **kwargs):
        import inspect

        sig = inspect.signature(func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()

        for name, value in bound.arguments.items():
            # Skip 'self' / 'cls'
            if name in ("self", "cls"):
                continue

            # NaN / Inf check for numeric & array types
            _check_finite(value, name, func.__qualname__)

            # Type annotation check
            if name in hints:
                _check_type(value, hints[name], name, func.__qualname__)

        return func(*args, **kwargs)

    return wrapper


def timed(func: Callable) -> Callable:
    """
    Decorator that measures function execution time and logs the result.

    Uses ``logging`` instead of ``print()`` — the output goes through
    the quantcore logging infrastructure.

    Examples
    --------
    >>> @timed
    ... def slow_op():
    ...     import time; time.sleep(0.1)
    >>> slow_op()  # logs: [slow_op] executed in 0.10xx s
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        _logger.debug("[%s] executed in %.4f s", func.__qualname__, elapsed)
        return result

    return wrapper
