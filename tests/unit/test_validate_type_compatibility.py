"""
Unit tests for the type validation script.

Tests the validate_type_compatibility.py script functionality.
"""

import pytest
import json
from pathlib import Path
import sys

# Add scripts to path for import
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from validate_type_compatibility import TypeValidator  # noqa: E402


@pytest.mark.unit
class TestTypeValidator:
    """Test the TypeValidator class."""

    @pytest.fixture
    def validator(self, temp_dir: Path) -> TypeValidator:
        """Create a TypeValidator instance with temp directories."""
        ollama_dir = temp_dir / "ollama-types"
        openai_dir = temp_dir / "openai-examples"
        ollama_dir.mkdir()
        openai_dir.mkdir()
        return TypeValidator(ollama_dir, openai_dir)

    def test_validator_initialization(self, validator: TypeValidator):
        """Test that validator initializes correctly."""
        assert validator.ollama_types_dir.exists()
        assert validator.openai_examples_dir.exists()
        assert "timestamp" in validator.validation_results
        assert "summary" in validator.validation_results
        assert validator.validation_results["summary"]["total_checks"] == 0

    def test_load_ollama_types(self, validator: TypeValidator):
        """Test loading Ollama type definitions."""
        # Create a mock types file
        types_file = validator.ollama_types_dir / "_types.py"
        types_file.write_text("# Mock Ollama types")

        types = validator.load_ollama_types()

        assert "_types" in types
        assert types["_types"]["exists"] is True
        assert str(types_file) in types["_types"]["file"]

    def test_load_openai_examples(self, validator: TypeValidator):
        """Test loading OpenAI response examples."""
        # Create mock example files
        models_data = {
            "response": {
                "object": "list",
                "data": [{"id": "gpt-3.5-turbo", "object": "model"}],
            }
        }

        models_file = validator.openai_examples_dir / "models.json"
        models_file.write_text(json.dumps(models_data))

        chat_dir = validator.openai_examples_dir / "chat"
        chat_dir.mkdir()
        chat_file = chat_dir / "example_test.json"
        chat_data = {"response": {"id": "chatcmpl-test", "object": "chat.completion"}}
        chat_file.write_text(json.dumps(chat_data))

        examples = validator.load_openai_examples()

        assert "models" in examples
        assert len(examples["models"]) == 1
        assert "chat/completions" in examples
        assert len(examples["chat/completions"]) == 1

    def test_validate_models_endpoint(self, validator: TypeValidator):
        """Test validation of models endpoint."""
        examples = [
            {
                "response": {
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
            }
        ]

        result = validator.validate_models_endpoint(examples)

        assert result["endpoint"] == "models"
        assert result["status"] == "pass"
        assert len(result["checks"]) > 0
        assert validator.validation_results["summary"]["total_checks"] > 0
        assert validator.validation_results["summary"]["passed"] > 0

    def test_validate_chat_endpoint(self, validator: TypeValidator):
        """Test validation of chat completions endpoint."""
        examples = [
            {
                "response": {
                    "id": "chatcmpl-test",
                    "object": "chat.completion",
                    "created": 1719947520,
                    "model": "gpt-3.5-turbo",
                    "choices": [
                        {
                            "index": 0,
                            "message": {"role": "assistant", "content": "Hello!"},
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {
                        "prompt_tokens": 10,
                        "completion_tokens": 5,
                        "total_tokens": 15,
                    },
                }
            }
        ]

        result = validator.validate_chat_endpoint(examples)

        assert result["endpoint"] == "chat/completions"
        assert result["status"] == "pass"
        assert len(result["checks"]) > 0

    def test_validate_embeddings_endpoint(self, validator: TypeValidator):
        """Test validation of embeddings endpoint."""
        examples = [
            {
                "response": {
                    "object": "list",
                    "data": [
                        {
                            "object": "embedding",
                            "index": 0,
                            "embedding": [0.1, 0.2, 0.3],
                        }
                    ],
                    "model": "text-embedding-ada-002",
                    "usage": {"prompt_tokens": 10, "total_tokens": 10},
                }
            }
        ]

        result = validator.validate_embeddings_endpoint(examples)

        assert result["endpoint"] == "embeddings"
        assert result["status"] == "pass"
        assert len(result["checks"]) > 0

    def test_validate_streaming_responses(self, validator: TypeValidator):
        """Test validation of streaming chat responses."""
        examples = [
            {
                "response_chunks": [
                    {
                        "id": "chatcmpl-stream",
                        "object": "chat.completion.chunk",
                        "created": 1719947540,
                        "model": "gpt-3.5-turbo",
                        "choices": [
                            {
                                "index": 0,
                                "delta": {"role": "assistant", "content": ""},
                                "finish_reason": None,
                            }
                        ],
                    },
                    {
                        "id": "chatcmpl-stream",
                        "object": "chat.completion.chunk",
                        "created": 1719947540,
                        "model": "gpt-3.5-turbo",
                        "choices": [
                            {
                                "index": 0,
                                "delta": {"content": "Hello"},
                                "finish_reason": None,
                            }
                        ],
                    },
                ]
            }
        ]

        result = validator.validate_streaming_responses(examples)

        assert result["endpoint"] == "chat/completions (streaming)"
        assert result["status"] == "pass"
        assert len(result["checks"]) > 0

    def test_generate_compatibility_notes(self, validator: TypeValidator):
        """Test generation of compatibility notes."""
        notes = validator.generate_compatibility_notes()

        assert isinstance(notes, list)
        assert len(notes) > 0
        assert any("tags" in note and "models" in note for note in notes)
        assert any("Parameter mappings" in note for note in notes)

    def test_validation_failure(self, validator: TypeValidator):
        """Test that validation correctly identifies failures."""
        # Example with missing required fields
        examples = [{"response": {"data": []}}]  # Missing "object" field

        result = validator.validate_models_endpoint(examples)

        assert result["status"] == "fail"
        assert validator.validation_results["summary"]["failed"] > 0

    def test_save_report(self, validator: TypeValidator, temp_dir: Path):
        """Test saving validation report."""
        output_file = temp_dir / "test-report.json"

        # Run some validation
        validator.validation_results["summary"]["total_checks"] = 10
        validator.validation_results["summary"]["passed"] = 8
        validator.validation_results["summary"]["failed"] = 2
        validator.validation_results["overall_status"] = "FAIL"

        validator.save_report(output_file)

        assert output_file.exists()

        with open(output_file, "r") as f:
            saved_data = json.load(f)

        assert saved_data["summary"]["total_checks"] == 10
        assert saved_data["summary"]["passed"] == 8
        assert saved_data["summary"]["failed"] == 2
        assert saved_data["overall_status"] == "FAIL"
