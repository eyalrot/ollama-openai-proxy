import structlog
import logging
import sys
import os
from structlog.stdlib import BoundLogger


def configure_logging(
    log_level: str = "INFO", environment: str = "production"
) -> structlog.stdlib.BoundLogger:
    """Configure structlog for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        environment: Environment name (production, development)

    Returns:
        Configured logger instance
    """
    # Set stdlib logging level
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    timestamper = structlog.processors.TimeStamper(fmt="iso")

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]

    if environment == "development":
        # Colored output for development
        formatter = structlog.dev.ConsoleRenderer()
    else:
        # JSON output for production
        formatter = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=shared_processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure the formatter for stdlib logging
    handler = logging.StreamHandler()
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=formatter,
            foreign_pre_chain=shared_processors,
        )
    )

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Create and return logger
    return structlog.get_logger()


def get_logger(name: str | None = None) -> BoundLogger:
    """Get a configured logger instance.

    Args:
        name: Logger name (defaults to module name)

    Returns:
        Configured logger instance
    """
    return structlog.get_logger(name)


# Configure logging on module import
logger = configure_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    environment=os.getenv("ENVIRONMENT", "production"),
)
