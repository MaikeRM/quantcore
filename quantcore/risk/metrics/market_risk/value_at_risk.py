from typing import Optional
import numpy as np
from quantcore.core.utils.config import get_config

class ValueAtRisk:
    """Calculates Value at Risk (VaR) using different methodologies."""
    
    def __init__(self, confidence_level: Optional[float] = None, horizon: Optional[int] = None):
        config = get_config().quantcore.risk.var
        self.confidence_level = confidence_level if confidence_level is not None else config.confidence_level
        self.horizon = horizon if horizon is not None else config.horizon_days
        
    def historical(self, returns: np.ndarray) -> float:
        """Calculate Historical VaR from an array of returns."""
        alpha = 1.0 - self.confidence_level
        var_1d = -np.percentile(returns, alpha * 100)
        return float(var_1d * np.sqrt(self.horizon))
        
    def parametric_normal(self, returns: np.ndarray) -> float:
        """Calculate Parametric Normal VaR."""
        from scipy.stats import norm
        mu = np.mean(returns)
        sigma = np.std(returns)
        alpha = 1.0 - self.confidence_level
        
        z_score = norm.ppf(alpha)
        var_1d = -(mu + z_score * sigma)
        return float(var_1d * np.sqrt(self.horizon))
