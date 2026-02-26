from typing import TypeAlias, Union, List
import numpy as np

# Basic financial type aliases
Price: TypeAlias = float
Volatility: TypeAlias = float
Rate: TypeAlias = float
TimeYears: TypeAlias = float
DiscountFactor: TypeAlias = float

# Arrays representation for vectorized operations
PriceArray: TypeAlias = Union[List[float], np.ndarray]
VolatilityArray: TypeAlias = Union[List[float], np.ndarray]
RateArray: TypeAlias = Union[List[float], np.ndarray]
TimeArray: TypeAlias = Union[List[float], np.ndarray]

# Probability paths (Monte Carlo simulations)
PathMatrix: TypeAlias = np.ndarray  # Expected shape: (n_paths, n_steps)
