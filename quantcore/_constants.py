"""
Global constants used across the quantcore library.
"""

from typing import Final
import numpy as np

# General precision limits
DEFAULT_EPSILON: Final[float] = 1e-10
DEFAULT_TOLERANCE: Final[float] = 1e-8

# Time constants
DAYS_IN_YEAR_360: Final[int] = 360
DAYS_IN_YEAR_365: Final[int] = 365
DAYS_IN_YEAR_BUS252: Final[int] = 252

# Missing values equivalent
NA_VALUE: Final[float] = np.nan
