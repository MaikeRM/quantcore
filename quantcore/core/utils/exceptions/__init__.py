"""
Custom exception hierarchy for the quantcore library.

All exceptions carry rich context: the parameter that caused the error,
the invalid value, an optional hint, and a structured representation
suitable for logging / serialisation.
"""

from typing import Any, Optional, Dict

__all__ = [
    "QuantcoreError",
    "ValidationError",
    "NumericalError",
    "ConvergenceError",
    "EngineNotFoundError",
    "ConfigurationError",
    "DataError",
]


class QuantcoreError(Exception):
    """
    Base exception for all quantcore library errors.

    Parameters
    ----------
    message : str
        Human-readable error description.
    context : dict, optional
        Arbitrary key-value pairs that describe the circumstances
        surrounding the error (e.g. ``{"module": "pricing", "step": 3}``).
    hint : str, optional
        A short suggestion on how to fix the problem.

    Examples
    --------
    >>> raise QuantcoreError(
    ...     "Something went wrong",
    ...     context={"module": "risk"},
    ...     hint="Check your input data.",
    ... )
    """

    def __init__(
        self,
        message: str = "",
        *,
        context: Optional[Dict[str, Any]] = None,
        hint: Optional[str] = None,
    ):
        self.raw_message = message
        self.context: Dict[str, Any] = context or {}
        self.hint = hint
        super().__init__(self._build_message())

    def _build_message(self) -> str:
        parts = [self.raw_message]

        if self.context:
            ctx_str = ", ".join(f"{k}={v!r}" for k, v in self.context.items())
            parts.append(f"  Context: {ctx_str}")

        if self.hint:
            parts.append(f"  Hint: {self.hint}")

        return "\n".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        """Structured representation for logging / serialisation."""
        return {
            "error_type": type(self).__name__,
            "message": self.raw_message,
            "context": self.context,
            "hint": self.hint,
        }

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}({self.raw_message!r}, "
            f"context={self.context!r}, hint={self.hint!r})"
        )


class ValidationError(QuantcoreError):
    """
    Raised when data validation fails.

    Extends ``QuantcoreError`` with the specific *parameter* and
    *invalid_value* that triggered the failure.

    Parameters
    ----------
    message : str
        Human-readable description.
    parameter : str, optional
        Name of the parameter that failed validation.
    invalid_value : Any, optional
        The offending value.
    function : str, optional
        Qualified name of the function where validation failed.
    """

    def __init__(
        self,
        message: str = "",
        *,
        parameter: Optional[str] = None,
        invalid_value: Any = None,
        function: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        hint: Optional[str] = None,
    ):
        self.parameter = parameter
        self.invalid_value = invalid_value
        self.function = function

        # Build enriched context automatically
        enriched_context = dict(context or {})
        if parameter is not None:
            enriched_context["parameter"] = parameter
        if invalid_value is not None:
            enriched_context["invalid_value"] = invalid_value
        if function is not None:
            enriched_context["function"] = function

        super().__init__(message, context=enriched_context, hint=hint)


class NumericalError(QuantcoreError):
    """
    Raised on numerical instabilities or NaN results.

    Parameters
    ----------
    message : str
        Human-readable description.
    operation : str, optional
        The mathematical operation that failed.
    """

    def __init__(
        self,
        message: str = "",
        *,
        operation: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        hint: Optional[str] = None,
    ):
        self.operation = operation

        enriched_context = dict(context or {})
        if operation is not None:
            enriched_context["operation"] = operation

        super().__init__(message, context=enriched_context, hint=hint)


class ConvergenceError(NumericalError):
    """
    Raised when a numerical solver fails to converge.

    Parameters
    ----------
    message : str
        Human-readable description.
    iterations : int, optional
        Number of iterations attempted before failure.
    tolerance : float, optional
        The convergence tolerance that was not met.
    last_value : float, optional
        The last computed value before giving up.
    """

    def __init__(
        self,
        message: str = "",
        *,
        iterations: Optional[int] = None,
        tolerance: Optional[float] = None,
        last_value: Optional[float] = None,
        operation: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        hint: Optional[str] = None,
    ):
        self.iterations = iterations
        self.tolerance = tolerance
        self.last_value = last_value

        enriched_context = dict(context or {})
        if iterations is not None:
            enriched_context["iterations"] = iterations
        if tolerance is not None:
            enriched_context["tolerance"] = tolerance
        if last_value is not None:
            enriched_context["last_value"] = last_value

        super().__init__(
            message,
            operation=operation,
            context=enriched_context,
            hint=hint or "Try increasing max_iterations or relaxing tolerance.",
        )


class EngineNotFoundError(QuantcoreError):
    """
    Raised when a requested pricing engine cannot be found or is unsupported.

    Parameters
    ----------
    message : str
        Human-readable description.
    instrument_type : str, optional
        The instrument type that was requested.
    engine_type : str, optional
        The engine type that was requested.
    """

    def __init__(
        self,
        message: str = "",
        *,
        instrument_type: Optional[str] = None,
        engine_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        hint: Optional[str] = None,
    ):
        self.instrument_type = instrument_type
        self.engine_type = engine_type

        enriched_context = dict(context or {})
        if instrument_type is not None:
            enriched_context["instrument_type"] = instrument_type
        if engine_type is not None:
            enriched_context["engine_type"] = engine_type

        super().__init__(
            message,
            context=enriched_context,
            hint=hint or "Register the engine with PricingEngineFactory.register_engine().",
        )


class ConfigurationError(QuantcoreError):
    """
    Raised when the configuration is invalid or missing.
    """

    def __init__(
        self,
        message: str = "",
        *,
        config_key: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        hint: Optional[str] = None,
    ):
        self.config_key = config_key

        enriched_context = dict(context or {})
        if config_key is not None:
            enriched_context["config_key"] = config_key

        super().__init__(
            message,
            context=enriched_context,
            hint=hint or "Check your config/default.yaml file.",
        )


class DataError(QuantcoreError):
    """
    Raised when market data is missing, corrupt, or unavailable.
    """

    def __init__(
        self,
        message: str = "",
        *,
        source: Optional[str] = None,
        ticker: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        hint: Optional[str] = None,
    ):
        self.source = source
        self.ticker = ticker

        enriched_context = dict(context or {})
        if source is not None:
            enriched_context["source"] = source
        if ticker is not None:
            enriched_context["ticker"] = ticker

        super().__init__(message, context=enriched_context, hint=hint)
