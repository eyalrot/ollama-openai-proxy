"""Unit tests for main FastAPI application."""

import pytest

from app.main import app


@pytest.mark.unit
class TestMainApplication:
    """Tests for main FastAPI application."""

    def test_app_metadata(self) -> None:
        """Test application metadata is correctly set."""
        assert app.title == "Ollama OpenAI Proxy"
        assert app.version == "0.1.0"
        assert "Ollama API calls to OpenAI API format" in app.description

    def test_cors_middleware_configured(self) -> None:
        """Test CORS middleware is configured."""
        # Test that CORS middleware is added to app
        middleware_found = False
        for middleware in app.user_middleware:
            if middleware.cls.__name__ == "CORSMiddleware":
                middleware_found = True
                break
        assert middleware_found, "CORS middleware not found in app"

    def test_docs_endpoints_available(self) -> None:
        """Test documentation endpoints are available."""
        # Test that docs URLs are configured
        assert app.docs_url == "/docs"
        assert app.redoc_url == "/redoc"
