from typing import Dict, Type, Optional, Any
from enum import Enum
import inspect
from quantcore.core.base.abc.instrument import FinancialInstrument
from quantcore.core.base.abc.pricer import PricingEngine
from .analytic.black_scholes import BlackScholesEngine
from quantcore.core.utils.exceptions import EngineNotFoundError

class EngineType(Enum):
    """Types of pricing engines available."""
    ANALYTIC = "analytic"
    BINOMIAL = "binomial"
    MONTE_CARLO = "monte_carlo"
    FINITE_DIFFERENCE = "finite_difference"

class PricingEngineFactory:
    """Factory for creating appropriate pricing engines dynamically."""
    
    _engine_registry: Dict[str, Type[PricingEngine]] = {}
    _default_engines: Dict[str, EngineType] = {}

    def __init__(self):
        self._register_default_engines()
        
    @classmethod
    def register_engine(cls, instrument_class: Type, engine_type: EngineType, engine_class: Type):
        key = f"{instrument_class.__name__}_{engine_type.value}"
        cls._engine_registry[key] = engine_class
        
    @classmethod
    def set_default_engine(cls, instrument_class: Type, engine_type: EngineType):
        cls._default_engines[instrument_class.__name__] = engine_type

    def _register_default_engines(self):
        from ...instruments.derivatives.options.european import EuropeanOption
        self.register_engine(EuropeanOption, EngineType.ANALYTIC, BlackScholesEngine)
        self.set_default_engine(EuropeanOption, EngineType.ANALYTIC)
        
    def create_engine(self, instrument: FinancialInstrument, engine_type: Optional[EngineType] = None, **kwargs) -> PricingEngine:
        if engine_type is None:
            engine_type = self._get_default_engine_type(instrument)
            
        instrument_class = type(instrument).__name__
        key = f"{instrument_class}_{engine_type.value}"
        
        if key not in self._engine_registry:
            raise EngineNotFoundError(f"No engine found for {instrument_class} with type {engine_type}")
            
        engine_class = self._engine_registry[key]
        return engine_class(**kwargs)
        
    def _get_default_engine_type(self, instrument: FinancialInstrument) -> EngineType:
        instrument_class = type(instrument).__name__
        if instrument_class in self._default_engines:
            return self._default_engines[instrument_class]
            
        raise EngineNotFoundError(f"No default engine declared for {instrument_class}")
