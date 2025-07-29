"""Integration test for application startup."""

import pytest
import subprocess
import time
import httpx


@pytest.mark.integration
class TestAppStartup:
    """Test application startup and basic functionality."""

    def test_app_starts_and_health_check_works(self) -> None:
        """Test that the app starts and health endpoint responds."""
        # Start the app
        process = subprocess.Popen(
            ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "11434"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        try:
            # Give the app time to start
            time.sleep(2)

            # Test health endpoint
            with httpx.Client() as client:
                response = client.get("http://localhost:11434/health")
                assert response.status_code == 200

                data = response.json()
                assert data["status"] == "healthy"
                assert data["version"] == "0.1.0"
                assert data["environment"] == "development"
                assert "timestamp" in data

                # Test CORS headers
                response = client.get(
                    "http://localhost:11434/health",
                    headers={"Origin": "http://example.com"},
                )
                assert response.status_code == 200
                assert response.headers.get("access-control-allow-origin") == "*"

        finally:
            # Clean up
            process.terminate()
            process.wait(timeout=5)
