"""
Logging infrastructure for the quantcore library.

Provides a configurable, structured logging system that replaces all
ad-hoc `print()` statements with proper logging facilities.

Usage
-----
    from quantcore.core.utils.logging import get_logger

    logger = get_logger(__name__)
    logger.info("Pricing completed", extra={"instrument": "EuropeanOption"})
"""

import logging
import sys
import json
from typing import Optional
from datetime import datetime, timezone


__all__ = [
    "get_logger",
    "setup_logging",
    "QuantcoreFormatter",
    "JSONFormatter",
    "LogLevel",
]


class LogLevel:
    """Convenience constants mirroring standard logging levels."""

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


# ── Default configuration ────────────────────────────────────────────
_DEFAULT_FORMAT = "[%(asctime)s] %(levelname)-8s %(name)s — %(message)s"
_DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_LIBRARY_ROOT_LOGGER = "quantcore"
_initialized = False


class QuantcoreFormatter(logging.Formatter):
    """
    Human-readable formatter with coloured level names for terminal output.

    Colour is only applied when the stream is a real TTY.
    """

    _COLOURS = {
        logging.DEBUG: "\033[36m",      # cyan
        logging.INFO: "\033[32m",       # green
        logging.WARNING: "\033[33m",    # yellow
        logging.ERROR: "\033[31m",      # red
        logging.CRITICAL: "\033[1;31m", # bold red
    }
    _RESET = "\033[0m"

    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None,
                 use_colour: bool = True):
        super().__init__(fmt=fmt or _DEFAULT_FORMAT,
                         datefmt=datefmt or _DEFAULT_DATE_FORMAT)
        self.use_colour = use_colour

    def format(self, record: logging.LogRecord) -> str:
        if self.use_colour and hasattr(sys.stderr, "isatty") and sys.stderr.isatty():
            colour = self._COLOURS.get(record.levelno, "")
            record.levelname = f"{colour}{record.levelname}{self._RESET}"
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """
    Structured JSON formatter suitable for log aggregation systems
    (e.g. ELK, Datadog, CloudWatch).
    """

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Merge any extra keys passed via `extra={...}`
        for key, value in record.__dict__.items():
            if key not in logging.LogRecord(
                "", 0, "", 0, "", (), None
            ).__dict__ and key not in payload:
                try:
                    json.dumps(value)  # ensure serialisable
                    payload[key] = value
                except (TypeError, ValueError):
                    payload[key] = repr(value)

        if record.exc_info and record.exc_info[0] is not None:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def setup_logging(
    level: int = logging.INFO,
    fmt: str = "human",
    stream=None,
) -> None:
    """
    Configure the root ``quantcore`` logger.

    Parameters
    ----------
    level : int
        Logging level (use ``LogLevel`` constants or stdlib ``logging``).
    fmt : str
        Format style — ``"human"`` for coloured terminal output,
        ``"json"`` for structured JSON lines.
    stream
        Output stream; defaults to ``sys.stderr``.
    """
    global _initialized

    root_logger = logging.getLogger(_LIBRARY_ROOT_LOGGER)
    root_logger.setLevel(level)

    # Avoid stacking duplicate handlers on repeated calls
    root_logger.handlers.clear()

    stream = stream or sys.stderr
    handler = logging.StreamHandler(stream)

    if fmt == "json":
        handler.setFormatter(JSONFormatter())
    else:
        use_colour = hasattr(stream, "isatty") and stream.isatty()
        handler.setFormatter(QuantcoreFormatter(use_colour=use_colour))

    handler.setLevel(level)
    root_logger.addHandler(handler)
    _initialized = True


def get_logger(name: str) -> logging.Logger:
    """
    Return a logger scoped under the ``quantcore`` namespace.

    On the first call the library logging is lazily initialised to INFO/human
    so that consumers see reasonable output even without explicit setup.

    Parameters
    ----------
    name : str
        Typically ``__name__`` of the calling module.

    Returns
    -------
    logging.Logger
    """
    global _initialized
    if not _initialized:
        # Lazy default initialisation (INFO, human-readable, stderr)
        setup_logging()

    return logging.getLogger(name)
