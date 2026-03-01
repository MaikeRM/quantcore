import sys
from quantcore.core.utils.config import get_config
from quantcore.risk.metrics.market_risk.value_at_risk import ValueAtRisk
from quantcore.pricing.engines.engine_factory import PricingEngineFactory

cfg = get_config()
print(f"Var Confidence: {cfg.quantcore.risk.var.confidence_level}")

var = ValueAtRisk()
print(f"Var Instance confidence: {var.confidence_level}")

class MockInstrument: pass
try:
    factory = PricingEngineFactory()
    engine_type = factory._get_default_engine_type(MockInstrument())
    print(f"Factory default engine for mock: {engine_type}")
except Exception as e:
    print(f"Factory exception expected: {e}")

