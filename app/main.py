"""Main FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app.config import settings
from app.handlers.health import router as health_router
from app.utils.errors import (
    ProxyException,
    proxy_exception_handler as handle_proxy_exception,
    validation_error_handler as handle_validation_error,
    generic_exception_handler as handle_generic_exception,
)
from app.utils.logging import get_logger
from app.utils.middleware import LoggingMiddleware

# Get logger (logging is already configured in utils/logging.py)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logger.info(
        "application_starting",
        app_name=settings.app_name,
        app_version=settings.app_version,
        environment=settings.environment,
        host=settings.host,
        port=settings.port,
    )

    yield

    # Shutdown
    logger.info("application_shutting_down", app_name=settings.app_name)


# Create FastAPI app instance
app = FastAPI(
    title="Ollama OpenAI Proxy",
    description=(
        "A proxy service that translates Ollama API calls to OpenAI API format"
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# Exception handlers
app.add_exception_handler(
    ProxyException, handle_proxy_exception  # type: ignore[arg-type]
)


app.add_exception_handler(RequestValidationError, handle_validation_error)
app.add_exception_handler(ValidationError, handle_validation_error)
app.add_exception_handler(Exception, handle_generic_exception)


# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Configure CORS middleware for development
# TODO: Restrict origins for production deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, tags=["health"])
