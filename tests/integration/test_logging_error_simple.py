"""Simple integration test for logging and error handling."""

import pytest
import httpx
from httpx._transports.asgi import ASGITransport

# Import the app directly
from app.main import app


def test_health_endpoint_with_logging():
    """Test that health endpoint works with logging middleware."""
    # Create client using httpx directly
    transport = ASGITransport(app=app)
    client = httpx.Client(transport=transport, base_url="http://test")
    
    response = client.get("/health")
    
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "environment" in data
    assert "timestamp" in data
    
    client.close()


def test_404_error_handling():
    """Test 404 error response format."""
    transport = ASGITransport(app=app)
    client = httpx.Client(transport=transport, base_url="http://test")
    
    response = client.get("/nonexistent-endpoint")
    
    assert response.status_code == 404
    assert "X-Request-ID" in response.headers
    
    client.close()


def test_custom_error_handling():
    """Test custom error handling."""
    from fastapi import APIRouter
    from app.utils.errors import ValidationException
    
    # Create a test router
    test_router = APIRouter()
    
    @test_router.get("/test-validation-error")
    async def test_error():
        raise ValidationException(
            "Test validation error",
            details={"field": "test_field"}
        )
    
    # Add router temporarily
    app.include_router(test_router)
    
    try:
        transport = ASGITransport(app=app)
        client = httpx.Client(transport=transport, base_url="http://test")
        response = client.get("/test-validation-error")
        
        assert response.status_code == 400
        assert "X-Request-ID" in response.headers
        
        data = response.json()
        assert data["error"] == "ValidationException"
        assert data["error_code"] == "VALIDATION_ERROR"
        assert data["message"] == "Test validation error"
        assert data["details"] == {"field": "test_field"}
        assert "request_id" in data
        
        client.close()
    finally:
        # Remove the test router
        app.routes = [r for r in app.routes if r.path != "/test-validation-error"]


def test_logging_levels():
    """Test that logging levels work correctly."""
    import os
    from app.utils.logging import configure_logging, get_logger
    
    # Test INFO level (default)
    logger = get_logger("test")
    logger.info("This should appear")
    logger.debug("This should not appear in INFO level")
    
    # Test DEBUG level
    os.environ["APP_LOG_LEVEL"] = "DEBUG"
    configure_logging(log_level="DEBUG", environment="production")
    logger = get_logger("test")
    logger.debug("This should appear in DEBUG level")
    
    # Reset
    os.environ["APP_LOG_LEVEL"] = "INFO"