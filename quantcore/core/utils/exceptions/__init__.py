class QuantcoreError(Exception):
    """Base exception for all quantcore library errors."""
    pass

class ValidationError(QuantcoreError):
    """Raised when data validation fails."""
    pass

class NumericalError(QuantcoreError):
    """Raised on numerical instabilities or NaN results."""
    pass

class ConvergenceError(NumericalError):
    """Raised when a numerical solver fails to converge."""
    pass

class EngineNotFoundError(QuantcoreError):
    """Raised when a requested pricing engine cannot be found or is unsupported."""
    pass
