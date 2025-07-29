"""
Pytest configuration and shared fixtures.

This module provides common fixtures and configuration for all tests.
"""

import json
import pytest
from pathlib import Path
from typing import Dict, Any
import structlog
from unittest.mock import Mock, AsyncMock
from httpx import AsyncClient

# Configure structured logging for tests
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)


@pytest.fixture
def project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def references_dir(project_root: Path) -> Path:
    """Get the references directory."""
    return project_root / "references"


@pytest.fixture
def ollama_types_dir(references_dir: Path) -> Path:
    """Get the Ollama types directory."""
    return references_dir / "ollama-types"


@pytest.fixture
def openai_examples_dir(references_dir: Path) -> Path:
    """Get the OpenAI examples directory."""
    return references_dir / "openai-examples"


@pytest.fixture
def mock_openai_models_response(openai_examples_dir: Path) -> Dict[str, Any]:
    """Load mock OpenAI models response."""
    models_file = openai_examples_dir / "models.json"
    if models_file.exists():
        with open(models_file, "r") as f:
            return json.load(f)
    # Return minimal mock if file doesn't exist
    return {
        "object": "list",
        "data": [
            {
                "id": "gpt-3.5-turbo",
                "object": "model",
                "created": 1677610602,
                "owned_by": "openai",
            }
        ],
    }


@pytest.fixture
def mock_openai_chat_response(openai_examples_dir: Path) -> Dict[str, Any]:
    """Load mock OpenAI chat completion response."""
    chat_file = openai_examples_dir / "chat" / "example_simple_single_turn.json"
    if chat_file.exists():
        with open(chat_file, "r") as f:
            data = json.load(f)
            return data.get("response", {})
    # Return minimal mock if file doesn't exist
    return {
        "id": "chatcmpl-test",
        "object": "chat.completion",
        "created": 1719947520,
        "model": "gpt-3.5-turbo",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Hello! How can I help you?",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 8, "total_tokens": 18},
    }


@pytest.fixture
def mock_ollama_client() -> Mock:
    """Create a mock Ollama client."""
    client = Mock()

    # Mock list method (tags endpoint)
    client.list = Mock(
        return_value={
            "models": [
                {
                    "name": "llama2:latest",
                    "model": "llama2:latest",
                    "modified_at": "2024-01-01T00:00:00Z",
                    "size": 3826793677,
                    "digest": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # noqa: E501
                    "details": {
                        "parent_model": "",
                        "format": "gguf",
                        "family": "llama",
                        "families": ["llama"],
                        "parameter_size": "7B",
                        "quantization_level": "Q4_0",
                    },
                }
            ]
        }
    )

    # Mock generate method
    client.generate = Mock(
        return_value={
            "model": "llama2:latest",
            "created_at": "2024-01-01T00:00:00Z",
            "response": "Hello! How can I help you today?",
            "done": True,
            "context": [1, 2, 3],
            "total_duration": 1000000000,
            "load_duration": 100000000,
            "prompt_eval_duration": 200000000,
            "eval_count": 10,
            "eval_duration": 700000000,
        }
    )

    # Mock chat method
    client.chat = Mock(
        return_value={
            "model": "llama2:latest",
            "created_at": "2024-01-01T00:00:00Z",
            "message": {
                "role": "assistant",
                "content": "Hello! How can I help you today?",
            },
            "done": True,
            "total_duration": 1000000000,
            "load_duration": 100000000,
            "prompt_eval_duration": 200000000,
            "eval_count": 10,
            "eval_duration": 700000000,
        }
    )

    # Mock embeddings method
    client.embeddings = Mock(return_value={"embedding": [0.1, 0.2, 0.3, 0.4, 0.5]})

    return client


@pytest.fixture
def mock_openai_client() -> Mock:
    """Create a mock OpenAI client."""
    client = Mock()

    # Mock models.list method
    models_mock = Mock()
    models_mock.list = Mock(
        return_value=Mock(
            data=[
                Mock(
                    id="gpt-3.5-turbo",
                    object="model",
                    created=1677610602,
                    owned_by="openai",
                )
            ]
        )
    )
    client.models = models_mock

    # Mock chat.completions.create method
    chat_mock = Mock()
    completions_mock = Mock()
    completions_mock.create = AsyncMock(
        return_value=Mock(
            id="chatcmpl-test",
            object="chat.completion",
            created=1719947520,
            model="gpt-3.5-turbo",
            choices=[
                Mock(
                    index=0,
                    message=Mock(
                        role="assistant", content="Hello! How can I help you?"
                    ),
                    finish_reason="stop",
                )
            ],
            usage=Mock(prompt_tokens=10, completion_tokens=8, total_tokens=18),
        )
    )
    chat_mock.completions = completions_mock
    client.chat = chat_mock

    # Mock embeddings.create method
    embeddings_mock = Mock()
    embeddings_mock.create = AsyncMock(
        return_value=Mock(
            object="list",
            data=[
                Mock(object="embedding", index=0, embedding=[0.1, 0.2, 0.3, 0.4, 0.5])
            ],
            model="text-embedding-ada-002",
            usage=Mock(prompt_tokens=10, total_tokens=10),
        )
    )
    client.embeddings = embeddings_mock

    return client


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for test files."""
    return tmp_path


@pytest.fixture
def logger() -> structlog.BoundLogger:
    """Get a structured logger for tests."""
    return structlog.get_logger(__name__)


@pytest.fixture
def test_app():
    """Create test FastAPI application."""
    from app.main import app

    return app


@pytest.fixture
def test_client(test_app):
    """Create synchronous test client."""
    # Import here to avoid circular imports
    from fastapi.testclient import TestClient

    # Create test client - pass app as positional argument
    client = TestClient(test_app)
    yield client
    client.close()


@pytest.fixture
async def async_client(test_app):
    """Create async test client."""
    from httpx._transports.asgi import ASGITransport

    # Create async client with ASGI transport for newer httpx versions
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def override_settings(monkeypatch):
    """Override configuration for tests."""

    def _override(**kwargs):
        for key, value in kwargs.items():
            monkeypatch.setenv(key, str(value))

    return _override


@pytest.fixture
def temp_test_data(tmp_path: Path) -> Dict[str, Path]:
    """Create temporary test data files."""
    data_dir = tmp_path / "test_data"
    data_dir.mkdir(exist_ok=True)

    # Create sample test files
    test_json = data_dir / "test.json"
    test_json.write_text(json.dumps({"test": "data"}))

    test_txt = data_dir / "test.txt"
    test_txt.write_text("Test content")

    return {"data_dir": data_dir, "json_file": test_json, "text_file": test_txt}


# Markers for different test types
def pytest_configure(config):
    """Configure pytest with custom markers.

    Available markers:
    - @pytest.mark.unit: Unit tests that test individual components
    - @pytest.mark.integration: Integration tests that test multiple components
    - @pytest.mark.slow: Tests that take a long time to run
    - @pytest.mark.requires_api_key: Tests that require API keys

    Usage:
        @pytest.mark.unit
        def test_something():
            pass

        @pytest.mark.integration
        @pytest.mark.asyncio
        async def test_api_endpoint():
            pass
    """
    config.addinivalue_line(
        "markers", "unit: Unit tests that test individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests that test multiple components"
    )
    config.addinivalue_line("markers", "slow: Tests that take a long time to run")
    config.addinivalue_line("markers", "requires_api_key: Tests that require API keys")
