"""
Structured logging configuration using structlog.

This module configures application-wide structured logging with:
- JSON output for production (machine-readable logs)
- Colored console output for development (human-readable logs)
- Request ID tracking for distributed tracing
- Consistent log formatting across the application
"""

import logging
import sys
from typing import Any

import structlog
from structlog.types import Processor


def setup_logging(log_level: str = "INFO", json_logs: bool = False) -> None:
    """
    Configure structured logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: If True, output logs in JSON format. If False, use console format with colors.

    Example:
        >>> setup_logging(log_level="DEBUG", json_logs=False)
    """
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=numeric_level,
    )

    # Disable noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)

    # Shared processors for all environments
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,  # Include context variables
        structlog.stdlib.add_log_level,  # Add log level
        structlog.stdlib.add_logger_name,  # Add logger name
        structlog.processors.TimeStamper(fmt="iso"),  # Add ISO timestamp
        structlog.stdlib.PositionalArgumentsFormatter(),  # Support positional args
        structlog.processors.StackInfoRenderer(),  # Render stack info if present
        structlog.processors.UnicodeDecoder(),  # Decode unicode
    ]

    if json_logs:
        # Production: JSON output for log aggregation systems
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,  # Format exceptions as dicts
            structlog.processors.JSONRenderer(),  # Render as JSON
        ]
    else:
        # Development: Colored console output for human readability
        processors = shared_processors + [
            structlog.processors.format_exc_info,  # Format exceptions
            structlog.dev.ConsoleRenderer(colors=True),  # Pretty console output with colors
        ]

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (usually __name__ of the module)

    Returns:
        Configured structured logger

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("user_login", user_id=123, ip="192.168.1.1")
    """
    return structlog.get_logger(name)


def add_request_context(request_id: str, **kwargs: Any) -> None:
    """
    Add contextual information to all subsequent log entries in this context.

    This is useful for adding request-specific information like request IDs,
    user IDs, or session IDs that should appear in all logs for a request.

    Args:
        request_id: Unique identifier for the request
        **kwargs: Additional context to add to logs

    Example:
        >>> add_request_context(request_id="abc123", user_id=456)
        >>> logger.info("processing_request")  # Will include request_id and user_id
    """
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id, **kwargs)


def clear_request_context() -> None:
    """Clear all contextual information from the current context."""
    structlog.contextvars.clear_contextvars()
