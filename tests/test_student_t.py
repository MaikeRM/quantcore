"""
Test the t-student distribution implementation.
"""
import pytest
import numpy as np
from quantcore.core.math.statistics.distributions.student_t import StudentTDistribution

def test_student_t_pdf():
    dist = StudentTDistribution(df=5, loc=0.0, scale=1.0)
    x = np.array([0.0])
    
    pdf_val = dist.pdf(x)
    assert pdf_val.shape == (1,)
    assert pdf_val[0] > 0.3  # Standard central density

def test_student_t_fit(rng):
    # Data from a t-distribution
    data = rng.standard_t(df=5, size=5000)
    
    # Fit using MLE
    fitted = StudentTDistribution.fit(data, method='mle')
    
    # Check if df is somewhat close to 5
    assert 3.0 < fitted.df < 7.0

def test_student_t_risk_measures():
    dist = StudentTDistribution(df=5, loc=0.0, scale=1.0)
    
    # Risk measures at 95% confidence (alpha = 0.05)
    var = dist.var(0.05)
    cvar = dist.cvar(0.05)
    
    # CVaR should be more extreme (more negative) than VaR
    assert cvar < var
