"""
Performance utilities for the quantcore library.

The ``timed`` decorator now lives in ``quantcore.core.utils.decorators``
to avoid duplication.  It is re-exported here for backward compatibility.
"""

import time

from .decorators import timed  # single source of truth
from .logging import get_logger

__all__ = ["timed", "Timer"]

_logger = get_logger(__name__)


class Timer:
    """
    Context manager for timing execution blocks.

    Examples
    --------
    >>> with Timer() as t:
    ...     heavy_computation()
    >>> logger.info(f"Took {t.elapsed:.3f} s")
    """

    def __init__(self):
        self.start = None
        self.elapsed = 0.0

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.perf_counter() - self.start
        _logger.debug("Timer block executed in %.4f s", self.elapsed)
