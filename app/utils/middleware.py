import time
import uuid
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars

logger = structlog.get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging with request ID injection."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details."""
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Clear any existing context and bind new request ID
        clear_contextvars()
        bind_contextvars(request_id=request_id)
        
        # Log request start
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params),
            headers={k: v for k, v in request.headers.items() 
                    if k.lower() not in ["authorization", "cookie"]}
        )
        
        # Process request
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Handle streaming responses
        if isinstance(response, StreamingResponse):
            # For streaming responses, we can't get the final status until streaming is done
            logger.info(
                "request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration=round(duration, 3),
                response_type="streaming"
            )
        else:
            # Log standard response
            logger.info(
                "request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration=round(duration, 3),
                response_type="standard"
            )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        # Clear context after request
        clear_contextvars()
        
        return response