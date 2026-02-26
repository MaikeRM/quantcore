from typing import Tuple, Optional
import numpy as np
from scipy import special
from ....base.abc.distribution import ContinuousDistribution
from ....utils.decorators import validate_input

class StudentTDistribution(ContinuousDistribution):
    """
    Student's t-distribution with adjustments for finance.
    
    Parameters
    ----------
    df : float
        Degrees of freedom (ν > 0)
    loc : float
        Location parameter
    scale : float
        Scale parameter (σ > 0)
    """
    
    def __init__(self, df: float, loc: float = 0.0, scale: float = 1.0):
        self.df = df
        self.loc = loc
        self.scale = scale
        self._validate_params()
        
    def _validate_params(self):
        if self.df <= 0:
            raise ValueError("Degrees of freedom must be positive")
        if self.scale <= 0:
            raise ValueError("Scale must be positive")
    
    @validate_input
    def pdf(self, x: np.ndarray) -> np.ndarray:
        """Probability density function."""
        z = (x - self.loc) / self.scale
        numerator = special.gamma((self.df + 1) / 2)
        denominator = (np.sqrt(self.df * np.pi) * special.gamma(self.df / 2) * 
                      self.scale)
        factor = numerator / denominator
        return factor * (1 + z**2 / self.df) ** (-(self.df + 1) / 2)
    
    @validate_input
    def cdf(self, x: np.ndarray) -> np.ndarray:
        """Cumulative distribution function."""
        z = (x - self.loc) / self.scale
        return special.stdtr(self.df, z)
    
    def ppf(self, q: np.ndarray) -> np.ndarray:
        """Percent point function (inverse CDF)."""
        return self.loc + self.scale * special.stdtrit(self.df, q)
    
    def moment(self, n: int) -> float:
        """n-th moment of the distribution."""
        if n % 2 == 1:  # Odd moments are 0 for symmetric t-dist
            return 0.0
        if n >= self.df:
            return np.inf
        
        k = n // 2
        moment = 1.0
        for i in range(k):
            moment *= (self.df - 2 * (i + 1))
        return (self.scale ** n) * moment
    
    @property
    def skewness(self) -> float:
        """Skewness (0 for symmetric t-distribution)."""
        return 0.0
    
    @property
    def kurtosis(self) -> float:
        """Excess kurtosis."""
        if self.df > 4:
            return 6 / (self.df - 4)
        elif self.df > 2:
            return np.inf
        else:
            return np.nan
    
    @classmethod
    def fit(cls, data: np.ndarray, method: str = 'mle') -> 'StudentTDistribution':
        """Fit distribution to data."""
        if method == 'mle':
            from scipy import optimize
            
            def neg_log_likelihood(params):
                df, loc, scale = params
                if df <= 0 or scale <= 0:
                    return np.inf
                dist = cls(df, loc, scale)
                return -np.sum(np.log(dist.pdf(data) + 1e-10))
            
            init_df = 5.0
            init_loc = np.median(data)
            init_scale = np.std(data, ddof=1)
            
            result = optimize.minimize(
                neg_log_likelihood,
                [init_df, init_loc, init_scale],
                bounds=[(2.1, 100), (None, None), (1e-10, None)]
            )
            
            df, loc, scale = result.x
            return cls(df, loc, scale)
        
        elif method == 'moment':
            mu = np.mean(data)
            sigma2 = np.var(data, ddof=1)
            excess_kurtosis = special.kurtosis(data, bias=False)
            
            if excess_kurtosis <= 0:
                df = np.inf
            else:
                df = 6 / excess_kurtosis + 4
            
            scale = np.sqrt(sigma2 * (df - 2) / df)
            return cls(df, mu, scale)
        
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def var(self, alpha: float = 0.05) -> float:
        """Value at Risk for given confidence level."""
        return self.ppf(alpha)
    
    def cvar(self, alpha: float = 0.05) -> float:
        """Conditional Value at Risk (Expected Shortfall)."""
        t_alpha = self.ppf(alpha)
        c = (self.df + t_alpha**2) / (self.df - 1)
        factor = special.gamma((self.df + 1) / 2) / (np.sqrt(np.pi * self.df) * 
                                                    special.gamma(self.df / 2))
        density = factor * (1 + t_alpha**2 / self.df) ** (-(self.df + 1) / 2)
        
        return self.loc - (self.scale * c * density / alpha)
