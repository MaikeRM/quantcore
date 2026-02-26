from typing import List, Tuple
import numpy as np
from scipy import interpolate
from ....core.base.abc.curve import Curve

class YieldCurve(Curve):
    """Basic representation of a Yield Curve with interpolation."""
    
    def __init__(self, times: np.ndarray, rates: np.ndarray, reference_date=None):
        if len(times) != len(rates):
            raise ValueError("Arrays must be of the same length.")
            
        self._reference_date = reference_date
        self.times = times
        self.rates = rates
        
        # Default fallback to Cubic Spline
        self._interp = interpolate.CubicSpline(times, rates, bc_type='natural')
        
    @property
    def reference_date(self):
        return self._reference_date
        
    def value(self, t: float) -> float:
        """Alias for zero_rate for base backwards compatibility."""
        return self.zero_rate(t)
        
    def zero_rate(self, t: float) -> float:
        """Returns the interpolated zero rate for time t."""
        # Extrapolation flat logic (if out of bounds)
        if t <= self.times[0]: return float(self.rates[0])
        if t >= self.times[-1]: return float(self.rates[-1])
        
        return float(self._interp(t))
        
    def forward_rate(self, t1: float, t2: float) -> float:
        """Continuous forward rate between t1 and t2."""
        if t1 >= t2: raise ValueError("t2 must be strictly greater than t1.")
        
        r1 = self.zero_rate(t1)
        r2 = self.zero_rate(t2)
        
        # f(t1,t2) = (r2*t2 - r1*t1)/(t2-t1)
        return (r2 * t2 - r1 * t1) / (t2 - t1)
        
    def discount_factor(self, t: float) -> float:
        """P(0, t) = exp(-r * t)"""
        r = self.zero_rate(t)
        return np.exp(-r * t)

class YieldCurveBuilder:
    """Builder class for yield curves from market instruments."""
    def bootstrap(self, market_instruments: List[Tuple[str, float, float]]) -> YieldCurve:
        """
        Simplistic deterministic bootstraper simulating the Readme builder structure. 
        Mock implementation for now.
        instruments should be: [(type, time, rate), ...]
        """
        # Sort by time
        sorted_inst = sorted(market_instruments, key=lambda x: x[1])
        times = np.array([x[1] for x in sorted_inst])
        rates = np.array([x[2] for x in sorted_inst])
        
        # In a real environment here we'd run an iterative solver minimizing spread
        return YieldCurve(times, rates)
