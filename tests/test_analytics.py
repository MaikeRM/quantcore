import pytest
import numpy as np
from quantcore.risk.metrics.market_risk.value_at_risk import ValueAtRisk
from quantcore.portfolio.construction.optimization.mean_variance import MeanVarianceOptimizer

def test_value_at_risk(rng):
    returns = rng.normal(0.001, 0.02, 1000)
    var_calc = ValueAtRisk(confidence_level=0.95, horizon=1)
    
    h_var = var_calc.historical(returns)
    p_var = var_calc.parametric_normal(returns)
    
    # Values should be somewhat close since generated from normal
    assert np.isclose(h_var, p_var, atol=0.01)
    # VaR should be positive meaning loss
    assert h_var > 0 
    assert p_var > 0

def test_mean_variance_optimization():
    # 3 Assets
    returns = np.array([0.05, 0.10, 0.12])
    cov = np.array([
        [0.010, 0.002, 0.004],
        [0.002, 0.040, 0.015],
        [0.004, 0.015, 0.060]
    ])
    
    optimizer = MeanVarianceOptimizer()
    
    # Min Var Portfolio
    w_min = optimizer.minimum_variance(returns, cov)
    assert np.isclose(np.sum(w_min), 1.0)
    assert all(w >= -1e-8 for w in w_min) # No short selling bound
    
    # The lowest variance asset is the first one (0.01), so it should have the highest weight
    assert np.argmax(w_min) == 0
    
    # Max Sharpe Portfolio
    w_shape = optimizer.maximum_sharpe(returns, cov, risk_free_rate=0.02)
    assert np.isclose(np.sum(w_shape), 1.0)
    assert all(w >= -1e-8 for w in w_shape)
