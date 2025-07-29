"""
Example integration tests demonstrating async testing patterns.

This module shows proper integration testing patterns including:
- Async test functions
- FastAPI test client usage
- Integration test markers
- Testing API endpoints
"""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_sync_health_endpoint(async_client: AsyncClient):
    """Test health endpoint using async client (updated due to httpx compatibility)."""
    # Act
    response = await async_client.get("/health")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data


@pytest.mark.integration
@pytest.mark.asyncio
async def test_async_health_endpoint(async_client: AsyncClient):
    """Test health endpoint using async client."""
    # Act
    response = await async_client.get("/health")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data


@pytest.mark.integration
@pytest.mark.asyncio
async def test_nonexistent_endpoint(async_client: AsyncClient):
    """Test that nonexistent endpoints return 404."""
    # Act
    response = await async_client.get("/this-does-not-exist")

    # Assert
    assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.asyncio
async def test_app_fixture(test_app):
    """Test that the app fixture provides the FastAPI instance."""
    from fastapi import FastAPI

    # Assert
    assert isinstance(test_app, FastAPI)
    assert test_app.title is not None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_multiple_async_requests(async_client: AsyncClient):
    """Test making multiple async requests."""
    # Act - make multiple requests
    responses = []
    for _ in range(3):
        response = await async_client.get("/health")
        responses.append(response)

    # Assert - all should succeed
    for response in responses:
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_request_headers(async_client: AsyncClient):
    """Test sending custom headers with requests."""
    # Arrange
    custom_headers = {"X-Test-Header": "test-value", "User-Agent": "Test-Client/1.0"}

    # Act
    response = await async_client.get("/health", headers=custom_headers)

    # Assert
    assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.slow  # Example of using multiple markers
@pytest.mark.asyncio
async def test_slow_operation_example(async_client: AsyncClient):
    """Example of a test marked as slow."""
    import asyncio

    # Simulate a slow operation
    await asyncio.sleep(0.1)

    # Act
    response = await async_client.get("/health")

    # Assert
    assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.asyncio
async def test_with_override_settings(async_client: AsyncClient, override_settings):
    """Test using the override_settings fixture."""
    # Arrange
    override_settings(APP_NAME="Test App", APP_VERSION="0.0.1-test")

    # Act
    response = await async_client.get("/health")

    # Assert
    assert response.status_code == 200
    # Note: The actual behavior depends on how the app uses these settings


@pytest.mark.integration
@pytest.mark.asyncio
class TestAsyncIntegrationClass:
    """Example async test class for integration tests."""

    async def test_health_check_in_class(self, async_client: AsyncClient):
        """Test health endpoint from within a test class."""
        # Act
        response = await async_client.get("/health")

        # Assert
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    async def test_json_response_format(self, async_client: AsyncClient):
        """Test that responses are valid JSON."""
        # Act
        response = await async_client.get("/health")

        # Assert
        assert response.headers["content-type"] == "application/json"

        # Should not raise an exception
        data = response.json()
        assert isinstance(data, dict)
