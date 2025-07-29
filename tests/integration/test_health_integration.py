"""Integration tests for health endpoint."""

import pytest
from datetime import datetime
import httpx
from httpx import ASGITransport

from app.main import app
from app.config import settings


@pytest.mark.integration
@pytest.mark.asyncio
class TestHealthEndpoint:
    """Integration tests for health check endpoint."""

    async def test_health_endpoint_returns_200(self) -> None:
        """Test health endpoint returns 200 status code."""
        # Test using httpx with ASGI transport
        transport = ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            response = await client.get("/health")
            assert response.status_code == 200

    async def test_health_response_format(self) -> None:
        """Test health endpoint response has correct format."""
        transport = ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            response = await client.get("/health")
            data = response.json()

            # Check all required fields are present
            assert "status" in data
            assert "version" in data
            assert "environment" in data
            assert "timestamp" in data

            # Check field values
            assert data["status"] == "healthy"
            assert data["version"] == settings.app_version
            assert data["environment"] == settings.environment

            # Check timestamp is valid ISO format
            timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
            assert isinstance(timestamp, datetime)

    async def test_health_endpoint_cors_headers(self) -> None:
        """Test health endpoint includes CORS headers."""
        transport = ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            response = await client.get(
                "/health",
                headers={"Origin": "http://example.com"},
            )
            assert response.status_code == 200
            assert "access-control-allow-origin" in response.headers
            assert response.headers["access-control-allow-origin"] == "*"

    async def test_full_application_startup(self) -> None:
        """Test full application can start and respond to requests."""
        transport = ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            # Make multiple requests to ensure app is stable
            for _ in range(3):
                response = await client.get("/health")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "healthy"
