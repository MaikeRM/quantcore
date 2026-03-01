from pydantic import BaseModel, Field, confloat
from typing import Optional, Dict

class CoreMathConfig(BaseModel):
    precision: str = "double"
    default_epsilon: float = 1e-10
    use_numba: bool = True
    parallel_threshold: int = 1000

class CoreTimeConfig(BaseModel):
    default_calendar: str = "Brazil"
    default_daycount: str = "bus252"
    date_format: str = "%Y-%m-%d"

class CoreUtilsValidationConfig(BaseModel):
    strict: bool = True
    raise_on_error: bool = True

class CoreUtilsCachingConfig(BaseModel):
    enabled: bool = True
    type: str = "lru"
    maxsize: int = 1024

class CoreUtilsConfig(BaseModel):
    validation: CoreUtilsValidationConfig
    caching: CoreUtilsCachingConfig

class CoreConfig(BaseModel):
    math: CoreMathConfig
    time: CoreTimeConfig
    utils: CoreUtilsConfig

class MarketDataConfig(BaseModel):
    default_source: str = "yahoo"
    cache_ttl: int = 3600
    retry_attempts: int = 3
    timeout: int = 30

class MarketCurvesConfig(BaseModel):
    interpolation: str = "cubic_spline"
    extrapolation: str = "flat"
    bootstrap_method: str = "iterative"

class MarketConfig(BaseModel):
    data: MarketDataConfig
    curves: MarketCurvesConfig

class EngineAnalyticConfig(BaseModel):
    precision: str = "high"

class EngineMonteCarloVarianceReductionConfig(BaseModel):
    antithetic: bool = True
    control_variates: bool = True
    importance_sampling: bool = False

class EngineMonteCarloConfig(BaseModel):
    default_paths: int = 10000
    default_steps: int = 252
    random_seed: int = 42
    variance_reduction: EngineMonteCarloVarianceReductionConfig

class EngineFiniteDifferenceConfig(BaseModel):
    grid_points: int = 100
    time_steps: int = 1000
    scheme: str = "crank_nicolson"

class EngineLatticeConfig(BaseModel):
    steps: int = 100
    method: str = "cox_ross_rubinstein"

class EnginesConfig(BaseModel):
    analytic: EngineAnalyticConfig
    monte_carlo: EngineMonteCarloConfig
    finite_difference: EngineFiniteDifferenceConfig
    lattice: EngineLatticeConfig

class PricingCalibrationConfig(BaseModel):
    default_method: str = "least_squares"
    default_optimizer: str = "levenberg_marquardt"
    max_iterations: int = 1000
    tolerance: float = 1e-8

class PricingConfig(BaseModel):
    default_engine: str = "auto"
    engines: EnginesConfig
    calibration: PricingCalibrationConfig

class RiskVarConfig(BaseModel):
    confidence_level: confloat(ge=0.0, le=1.0) = 0.95
    horizon_days: int = 1
    method: str = "historical"

class RiskGreeksConfig(BaseModel):
    bump_size: float = 0.01
    method: str = "analytic"

class RiskConfig(BaseModel):
    var: RiskVarConfig
    greeks: RiskGreeksConfig

class PortfolioOptimizationConfig(BaseModel):
    solver: str = "quadratic"
    max_iterations: int = 1000
    tolerance: float = 1e-6

class PortfolioConfig(BaseModel):
    optimization: PortfolioOptimizationConfig

class PerformanceConfig(BaseModel):
    use_multiprocessing: bool = True
    max_workers: int = 4
    chunk_size: int = 1000
    memory_limit_gb: int = 4

class LoggingHandlerConfig(BaseModel):
    enabled: bool = True
    path: Optional[str] = None
    max_size_mb: Optional[int] = None
    backup_count: Optional[int] = None

class LoggingHandlersConfig(BaseModel):
    console: LoggingHandlerConfig
    file: Optional[LoggingHandlerConfig] = None

class LoggingConfig(BaseModel):
    level: str = "INFO"
    format: str = "json"
    handlers: LoggingHandlersConfig

class MonitoringMetricsConfig(BaseModel):
    enabled: bool = True
    port: int = 9090

class MonitoringTracingConfig(BaseModel):
    enabled: bool = False

class MonitoringConfig(BaseModel):
    metrics: MonitoringMetricsConfig
    tracing: MonitoringTracingConfig

class QuantcoreConfig(BaseModel):
    version: str
    core: CoreConfig
    market: MarketConfig
    pricing: PricingConfig
    risk: RiskConfig
    portfolio: PortfolioConfig
    performance: PerformanceConfig
    logging: LoggingConfig
    monitoring: MonitoringConfig

class RootConfig(BaseModel):
    quantcore: QuantcoreConfig
