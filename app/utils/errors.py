from typing import Optional, Dict, Any
from pydantic import BaseModel
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import structlog

logger = structlog.get_logger(__name__)


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None


class ProxyException(HTTPException):
    """Base exception for all proxy errors."""
    error_code = "PROXY_ERROR"
    status_code = 500
    
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None
    ):
        self.message = message
        self.details = details
        if status_code:
            self.status_code = status_code
        super().__init__(status_code=self.status_code, detail=message)
    
    def to_error_response(self, request_id: Optional[str] = None) -> ErrorResponse:
        """Convert exception to error response model."""
        return ErrorResponse(
            error=self.__class__.__name__,
            error_code=self.error_code,
            message=self.message,
            details=self.details,
            request_id=request_id
        )


class ValidationException(ProxyException):
    """Validation errors."""
    error_code = "VALIDATION_ERROR"
    status_code = 400


class UpstreamException(ProxyException):
    """Errors from upstream services."""
    error_code = "UPSTREAM_ERROR"
    status_code = 502


class ConfigurationException(ProxyException):
    """Configuration errors."""
    error_code = "CONFIG_ERROR"
    status_code = 500


class NotImplementedException(ProxyException):
    """Feature not implemented."""
    error_code = "NOT_IMPLEMENTED"
    status_code = 501


async def proxy_exception_handler(request: Request, exc: ProxyException) -> JSONResponse:
    """Handle ProxyException and return standard error response."""
    request_id = getattr(request.state, "request_id", None)
    error_response = exc.to_error_response(request_id)
    
    logger.error(
        "proxy_exception",
        error_code=exc.error_code,
        status_code=exc.status_code,
        message=exc.message,
        details=exc.details,
        request_id=request_id,
        path=request.url.path,
        method=request.method
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(exclude_none=True)
    )


async def validation_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle Pydantic validation errors."""
    from pydantic import ValidationError
    
    request_id = getattr(request.state, "request_id", None)
    
    if isinstance(exc, ValidationError):
        errors = exc.errors()
        error_response = ErrorResponse(
            error="ValidationError",
            error_code="VALIDATION_ERROR",
            message="Request validation failed",
            details={"errors": errors},
            request_id=request_id
        )
        status_code = 400
    else:
        error_response = ErrorResponse(
            error="ValidationException",
            error_code="VALIDATION_ERROR",
            message=str(exc),
            request_id=request_id
        )
        status_code = 400
    
    logger.error(
        "validation_error",
        error_code="VALIDATION_ERROR",
        status_code=status_code,
        errors=error_response.details,
        request_id=request_id,
        path=request.url.path,
        method=request.method
    )
    
    return JSONResponse(
        status_code=status_code,
        content=error_response.model_dump(exclude_none=True)
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle generic exceptions."""
    request_id = getattr(request.state, "request_id", None)
    
    error_response = ErrorResponse(
        error=exc.__class__.__name__,
        error_code="INTERNAL_ERROR",
        message="An unexpected error occurred",
        request_id=request_id
    )
    
    logger.exception(
        "unhandled_exception",
        error_code="INTERNAL_ERROR",
        status_code=500,
        exception_type=exc.__class__.__name__,
        request_id=request_id,
        path=request.url.path,
        method=request.method
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump(exclude_none=True)
    )