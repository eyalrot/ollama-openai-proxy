"""Unit tests for error handling."""

import pytest
from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError, BaseModel
from unittest.mock import MagicMock

from app.utils.errors import (
    ErrorResponse,
    ProxyException,
    ValidationException,
    UpstreamException,
    ConfigurationException,
    NotImplementedException,
    proxy_exception_handler,
    validation_error_handler,
    generic_exception_handler,
)


class TestErrorModels:
    """Test error response models."""

    def test_error_response_model(self):
        """Test ErrorResponse model creation."""
        error = ErrorResponse(
            error="TestError",
            error_code="TEST_ERROR",
            message="Test error message",
            details={"key": "value"},
            request_id="test-123",
        )

        assert error.error == "TestError"
        assert error.error_code == "TEST_ERROR"
        assert error.message == "Test error message"
        assert error.details == {"key": "value"}
        assert error.request_id == "test-123"

    def test_error_response_model_minimal(self):
        """Test ErrorResponse with minimal fields."""
        error = ErrorResponse(
            error="TestError", error_code="TEST_ERROR", message="Test error message"
        )

        assert error.error == "TestError"
        assert error.error_code == "TEST_ERROR"
        assert error.message == "Test error message"
        assert error.details is None
        assert error.request_id is None


class TestExceptionClasses:
    """Test custom exception classes."""

    def test_proxy_exception(self):
        """Test ProxyException creation and attributes."""
        exc = ProxyException("Test error", details={"key": "value"})

        assert exc.message == "Test error"
        assert exc.details == {"key": "value"}
        assert exc.status_code == 500
        assert exc.error_code == "PROXY_ERROR"

    def test_proxy_exception_custom_status(self):
        """Test ProxyException with custom status code."""
        exc = ProxyException("Test error", status_code=503)

        assert exc.status_code == 503

    def test_validation_exception(self):
        """Test ValidationException attributes."""
        exc = ValidationException("Validation failed")

        assert exc.message == "Validation failed"
        assert exc.status_code == 400
        assert exc.error_code == "VALIDATION_ERROR"

    def test_upstream_exception(self):
        """Test UpstreamException attributes."""
        exc = UpstreamException("Upstream service error")

        assert exc.message == "Upstream service error"
        assert exc.status_code == 502
        assert exc.error_code == "UPSTREAM_ERROR"

    def test_configuration_exception(self):
        """Test ConfigurationException attributes."""
        exc = ConfigurationException("Config error")

        assert exc.message == "Config error"
        assert exc.status_code == 500
        assert exc.error_code == "CONFIG_ERROR"

    def test_not_implemented_exception(self):
        """Test NotImplementedException attributes."""
        exc = NotImplementedException("Feature not implemented")

        assert exc.message == "Feature not implemented"
        assert exc.status_code == 501
        assert exc.error_code == "NOT_IMPLEMENTED"

    def test_to_error_response(self):
        """Test converting exception to error response."""
        exc = ValidationException("Invalid input", details={"field": "missing"})
        response = exc.to_error_response(request_id="test-123")

        assert response.error == "ValidationException"
        assert response.error_code == "VALIDATION_ERROR"
        assert response.message == "Invalid input"
        assert response.details == {"field": "missing"}
        assert response.request_id == "test-123"


class TestExceptionHandlers:
    """Test exception handler functions."""

    @pytest.fixture
    def mock_request(self):
        """Create mock request with state."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.state.request_id = "test-request-id"
        request.url.path = "/test/path"
        request.method = "POST"
        return request

    @pytest.mark.asyncio
    async def test_proxy_exception_handler(self, mock_request):
        """Test proxy exception handler."""
        exc = ValidationException("Test validation error", details={"field": "value"})

        response = await proxy_exception_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400

        # Check response content
        import json

        content = json.loads(response.body.decode())
        assert content["error"] == "ValidationException"
        assert content["error_code"] == "VALIDATION_ERROR"
        assert content["message"] == "Test validation error"
        assert content["details"] == {"field": "value"}
        assert content["request_id"] == "test-request-id"

    @pytest.mark.asyncio
    async def test_proxy_exception_handler_no_request_id(self, mock_request):
        """Test proxy exception handler without request ID."""
        # Remove request_id attribute to simulate missing request ID
        delattr(mock_request.state, "request_id")
        exc = ProxyException("Test error")

        response = await proxy_exception_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500

        import json

        content = json.loads(response.body.decode())
        assert "request_id" not in content

    @pytest.mark.asyncio
    async def test_validation_error_handler_pydantic(self, mock_request):
        """Test validation error handler with Pydantic ValidationError."""

        # Create a Pydantic validation error
        class TestModel(BaseModel):
            field: str

        try:
            TestModel(field=123)  # This will raise ValidationError
        except ValidationError as exc:
            response = await validation_error_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400

        import json

        content = json.loads(response.body.decode())
        assert content["error"] == "ValidationError"
        assert content["error_code"] == "VALIDATION_ERROR"
        assert content["message"] == "Request validation failed"
        assert "errors" in content["details"]
        assert len(content["details"]["errors"]) > 0

    @pytest.mark.asyncio
    async def test_validation_error_handler_generic(self, mock_request):
        """Test validation error handler with generic exception."""
        exc = Exception("Generic validation error")

        response = await validation_error_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400

        import json

        content = json.loads(response.body.decode())
        assert content["error"] == "ValidationException"
        assert content["error_code"] == "VALIDATION_ERROR"
        assert content["message"] == "Generic validation error"

    @pytest.mark.asyncio
    async def test_generic_exception_handler(self, mock_request):
        """Test generic exception handler."""
        exc = RuntimeError("Unexpected error")

        response = await generic_exception_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500

        import json

        content = json.loads(response.body.decode())
        assert content["error"] == "RuntimeError"
        assert content["error_code"] == "INTERNAL_ERROR"
        assert content["message"] == "An unexpected error occurred"
        assert content["request_id"] == "test-request-id"
