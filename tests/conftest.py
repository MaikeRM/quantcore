import pytest
import numpy as np
import pandas as pd

class QuantcoreConfig:
    def __init__(self, math_precision: str, use_numba: bool, strict_validation: bool):
        self.math_precision = math_precision
        self.use_numba = use_numba
        self.strict_validation = strict_validation

@pytest.fixture(scope="session")
def config():
    """Global configuration for tests."""
    return QuantcoreConfig(
        math_precision="double",
        use_numba=False,  # Disable for faster tests
        strict_validation=True
    )

@pytest.fixture
def rng():
    """Random number generator with fixed seed for reproducibility."""
    return np.random.RandomState(42)

@pytest.fixture
def sample_equity_data(rng):
    """Sample equity price data."""
    n = 252  # One year of daily data
    returns = rng.normal(0.0005, 0.02, n)
    prices = 100 * np.exp(np.cumsum(returns))
    dates = pd.date_range('2023-01-01', periods=n, freq='B')
    return pd.Series(prices, index=dates, name='price')

@pytest.fixture
def sample_option_params():
    """Sample option parameters for testing."""
    return {
        'underlying_price': 100.0,
        'strike_price': 105.0,
        'time_to_maturity': 0.5,
        'risk_free_rate': 0.03,
        'volatility': 0.25,
        'dividend_yield': 0.0
    }

@pytest.fixture
def arb_free_option_params(rng):
    """Generate arbitrage-free option parameters."""
    S = rng.uniform(50, 150)
    K = rng.uniform(50, 150)
    T = rng.uniform(0.1, 2.0)
    r = rng.uniform(0.0, 0.05)
    sigma = rng.uniform(0.1, 0.5)
    
    return {
        'underlying_price': S,
        'strike_price': K,
        'time_to_maturity': T,
        'risk_free_rate': r,
        'volatility': sigma
    }
