import numpy as np
from scipy.optimize import minimize

class MeanVarianceOptimizer:
    """Markowitz Mean-Variance Portfolio Optimization."""
    
    def __init__(self, bounds=(0, 1)):
        # Default bounds: no short selling (0 to 1 weighting per asset)
        self.bounds = bounds
        
    def minimum_variance(self, expected_returns: np.ndarray, covariance_matrix: np.ndarray) -> np.ndarray:
        """Finds the portfolio with the absolute minimum variance."""
        n_assets = len(expected_returns)
        
        def obj_func(weights):
            return np.dot(weights.T, np.dot(covariance_matrix, weights))
            
        constraints = [
            {'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1.0}  # Weights sum to 1
        ]
        
        bounds = tuple(self.bounds for _ in range(n_assets))
        initial_guess = np.ones(n_assets) / n_assets
        
        result = minimize(obj_func, initial_guess, bounds=bounds, constraints=constraints)
        if not result.success:
            raise ValueError(f"Optimization failed: {result.message}")
            
        return result.x

    def maximum_sharpe(self, expected_returns: np.ndarray, covariance_matrix: np.ndarray, risk_free_rate: float = 0.0) -> np.ndarray:
        """Finds the tangency portfolio (maximum Sharpe ratio)."""
        n_assets = len(expected_returns)
        
        def obj_func(weights):
            ret = np.dot(weights.T, expected_returns)
            vol = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
            sharpe = (ret - risk_free_rate) / vol
            return -sharpe # Minimize negative sharpe
            
        constraints = [
            {'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1.0}
        ]
        
        bounds = tuple(self.bounds for _ in range(n_assets))
        initial_guess = np.ones(n_assets) / n_assets
        
        result = minimize(obj_func, initial_guess, bounds=bounds, constraints=constraints)
        if not result.success:
            raise ValueError(f"Optimization failed: {result.message}")
            
        return result.x
