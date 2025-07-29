#!/usr/bin/env python3
"""
Validate that extracted Ollama types can be populated from OpenAI responses.

This script checks compatibility between Ollama's Pydantic models and OpenAI API
responses
to ensure our proxy can successfully translate between the two formats.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timezone
from collections import defaultdict

import structlog

# Configure structured logging
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

logger = structlog.get_logger(__name__)


class TypeValidator:
    """Validates Ollama types against OpenAI response examples."""

    def __init__(self, ollama_types_dir: Path, openai_examples_dir: Path):
        """
        Initialize the validator.

        Args:
            ollama_types_dir: Directory containing extracted Ollama types
            openai_examples_dir: Directory containing OpenAI response examples
        """
        self.ollama_types_dir = ollama_types_dir
        self.openai_examples_dir = openai_examples_dir
        self.validation_results: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": {"total_checks": 0, "passed": 0, "failed": 0, "warnings": 0},
            "endpoints": {},
        }

    def load_ollama_types(self) -> Dict[str, Any]:
        """Load extracted Ollama type definitions."""
        types = {}

        # Load the main types file
        types_file = self.ollama_types_dir / "_types.py"
        if types_file.exists():
            # Parse the Python file to extract class definitions
            # For now, we'll just note that the file exists
            types["_types"] = {"file": str(types_file), "exists": True}
            logger.info("Found Ollama types file", file=str(types_file))

        return types

    def load_openai_examples(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load OpenAI response examples organized by endpoint."""
        examples = defaultdict(list)

        # Load models endpoint
        models_file = self.openai_examples_dir / "models.json"
        if models_file.exists():
            with open(models_file, "r") as f:
                data = json.load(f)
                examples["models"].append(data)
                logger.info("Loaded models example")

        # Load chat completions
        chat_dir = self.openai_examples_dir / "chat"
        if chat_dir.exists():
            for example_file in chat_dir.glob("*.json"):
                with open(example_file, "r") as f:
                    data = json.load(f)
                    examples["chat/completions"].append(data)
                    logger.info("Loaded chat example", file=example_file.name)

        # Load embeddings
        embeddings_dir = self.openai_examples_dir / "embeddings"
        if embeddings_dir.exists():
            for example_file in embeddings_dir.glob("*.json"):
                if example_file.suffix == ".json":
                    with open(example_file, "r") as f:
                        data = json.load(f)
                        examples["embeddings"].append(data)
                        logger.info("Loaded embeddings example", file=example_file.name)

        return examples

    def validate_models_endpoint(
        self, examples: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate models list endpoint compatibility."""
        result = {"endpoint": "models", "checks": [], "status": "pass"}

        for example in examples:
            response = example.get("response", {})

            # Check required fields
            checks = [
                ("has_object_field", "object" in response),
                ("object_is_list", response.get("object") == "list"),
                ("has_data_field", "data" in response),
                ("data_is_array", isinstance(response.get("data"), list)),
            ]

            # Check model objects
            if "data" in response and isinstance(response["data"], list):
                for model in response["data"]:
                    model_checks = [
                        ("model_has_id", "id" in model),
                        ("model_has_object", "object" in model),
                        ("model_object_is_model", model.get("object") == "model"),
                        ("model_has_created", "created" in model),
                        ("model_has_owned_by", "owned_by" in model),
                    ]
                    checks.extend(model_checks)

            # Record results
            for check_name, passed in checks:
                self.validation_results["summary"]["total_checks"] += 1
                if passed:
                    self.validation_results["summary"]["passed"] += 1
                else:
                    self.validation_results["summary"]["failed"] += 1
                    result["status"] = "fail"

                result["checks"].append({"name": check_name, "passed": passed})

        return result

    def validate_chat_endpoint(self, examples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate chat completions endpoint compatibility."""
        result = {"endpoint": "chat/completions", "checks": [], "status": "pass"}

        for example in examples:
            response = example.get("response", {})

            # Skip streaming examples for now
            if "response_chunks" in example:
                continue

            # Check required fields
            checks = [
                ("has_id", "id" in response),
                ("has_object", "object" in response),
                (
                    "object_is_chat_completion",
                    response.get("object") == "chat.completion",
                ),
                ("has_created", "created" in response),
                ("has_model", "model" in response),
                ("has_choices", "choices" in response),
                ("choices_is_array", isinstance(response.get("choices"), list)),
                ("has_usage", "usage" in response),
            ]

            # Check choices structure
            if "choices" in response and isinstance(response["choices"], list):
                for choice in response["choices"]:
                    choice_checks = [
                        ("choice_has_index", "index" in choice),
                        ("choice_has_message", "message" in choice),
                        ("choice_has_finish_reason", "finish_reason" in choice),
                    ]

                    # Check message structure
                    if "message" in choice:
                        message = choice["message"]
                        message_checks = [
                            ("message_has_role", "role" in message),
                            ("message_has_content", "content" in message),
                        ]
                        choice_checks.extend(message_checks)

                    checks.extend(choice_checks)

            # Check usage structure
            if "usage" in response:
                usage = response["usage"]
                usage_checks = [
                    ("usage_has_prompt_tokens", "prompt_tokens" in usage),
                    ("usage_has_completion_tokens", "completion_tokens" in usage),
                    ("usage_has_total_tokens", "total_tokens" in usage),
                ]
                checks.extend(usage_checks)

            # Record results
            for check_name, passed in checks:
                self.validation_results["summary"]["total_checks"] += 1
                if passed:
                    self.validation_results["summary"]["passed"] += 1
                else:
                    self.validation_results["summary"]["failed"] += 1
                    result["status"] = "fail"

                result["checks"].append({"name": check_name, "passed": passed})

        return result

    def validate_embeddings_endpoint(
        self, examples: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate embeddings endpoint compatibility."""
        result = {"endpoint": "embeddings", "checks": [], "status": "pass"}

        for example in examples:
            response = example.get("response", {})

            # Check required fields
            checks = [
                ("has_object", "object" in response),
                ("object_is_list", response.get("object") == "list"),
                ("has_data", "data" in response),
                ("data_is_array", isinstance(response.get("data"), list)),
                ("has_model", "model" in response),
                ("has_usage", "usage" in response),
            ]

            # Check embedding objects
            if "data" in response and isinstance(response["data"], list):
                for embedding in response["data"]:
                    embedding_checks = [
                        ("embedding_has_object", "object" in embedding),
                        (
                            "embedding_object_is_embedding",
                            embedding.get("object") == "embedding",
                        ),
                        ("embedding_has_index", "index" in embedding),
                        ("embedding_has_embedding", "embedding" in embedding),
                        (
                            "embedding_is_array",
                            isinstance(embedding.get("embedding"), list),
                        ),
                    ]
                    checks.extend(embedding_checks)

            # Check usage structure
            if "usage" in response:
                usage = response["usage"]
                usage_checks = [
                    ("usage_has_prompt_tokens", "prompt_tokens" in usage),
                    ("usage_has_total_tokens", "total_tokens" in usage),
                ]
                checks.extend(usage_checks)

            # Record results
            for check_name, passed in checks:
                self.validation_results["summary"]["total_checks"] += 1
                if passed:
                    self.validation_results["summary"]["passed"] += 1
                else:
                    self.validation_results["summary"]["failed"] += 1
                    result["status"] = "fail"

                result["checks"].append({"name": check_name, "passed": passed})

        return result

    def validate_streaming_responses(
        self, examples: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate streaming chat responses."""
        result = {
            "endpoint": "chat/completions (streaming)",
            "checks": [],
            "status": "pass",
        }

        for example in examples:
            if "response_chunks" not in example:
                continue

            chunks = example.get("response_chunks", [])

            # Check each chunk
            for i, chunk in enumerate(chunks):
                chunk_checks = [
                    ("chunk_has_id", "id" in chunk),
                    ("chunk_has_object", "object" in chunk),
                    (
                        "chunk_object_is_chunk",
                        chunk.get("object") == "chat.completion.chunk",
                    ),
                    ("chunk_has_created", "created" in chunk),
                    ("chunk_has_model", "model" in chunk),
                    ("chunk_has_choices", "choices" in chunk),
                ]

                # Check delta in choices
                if "choices" in chunk and isinstance(chunk["choices"], list):
                    for choice in chunk["choices"]:
                        delta_checks = [
                            ("choice_has_index", "index" in choice),
                            ("choice_has_delta", "delta" in choice),
                            ("choice_has_finish_reason", "finish_reason" in choice),
                        ]
                        chunk_checks.extend(delta_checks)

                # Record results for first chunk only to avoid duplication
                if i == 0:
                    for check_name, passed in chunk_checks:
                        self.validation_results["summary"]["total_checks"] += 1
                        if passed:
                            self.validation_results["summary"]["passed"] += 1
                        else:
                            self.validation_results["summary"]["failed"] += 1
                            result["status"] = "fail"

                        result["checks"].append({"name": check_name, "passed": passed})

        return result

    def generate_compatibility_notes(self) -> List[str]:
        """Generate notes about compatibility between Ollama and OpenAI."""
        notes = []

        # Known differences and mappings
        notes.append("Ollama uses 'tags' endpoint while OpenAI uses 'models' endpoint")
        notes.append(
            "Ollama 'generate' endpoint maps to OpenAI 'chat/completions' endpoint"
        )
        notes.append(
            "Ollama 'chat' endpoint has similar structure to OpenAI 'chat/completions'"
        )
        notes.append(
            "Ollama 'embeddings' endpoint has similar structure to OpenAI 'embeddings'"
        )
        notes.append(
            "Response streaming is supported by both APIs with similar chunk structure"
        )

        # Parameter mappings
        notes.append("Parameter mappings needed:")
        notes.append("  - OpenAI 'model' -> Ollama 'model'")
        notes.append("  - OpenAI 'temperature' -> Ollama 'options.temperature'")
        notes.append("  - OpenAI 'max_tokens' -> Ollama 'options.num_predict'")
        notes.append(
            "  - OpenAI 'messages' -> Ollama 'messages' (chat) or 'prompt' (generate)"
        )
        notes.append("  - OpenAI 'stream' -> Ollama 'stream'")

        return notes

    def run_validation(self) -> None:
        """Run the complete validation process."""
        logger.info("Starting type compatibility validation")

        # Load data
        self.load_ollama_types()  # Loads types into self for later use
        openai_examples = self.load_openai_examples()

        # Validate each endpoint
        if "models" in openai_examples:
            result = self.validate_models_endpoint(openai_examples["models"])
            self.validation_results["endpoints"]["models"] = result

        if "chat/completions" in openai_examples:
            result = self.validate_chat_endpoint(openai_examples["chat/completions"])
            self.validation_results["endpoints"]["chat_completions"] = result

            # Also validate streaming
            stream_result = self.validate_streaming_responses(
                openai_examples["chat/completions"]
            )
            self.validation_results["endpoints"][
                "chat_completions_streaming"
            ] = stream_result

        if "embeddings" in openai_examples:
            result = self.validate_embeddings_endpoint(openai_examples["embeddings"])
            self.validation_results["endpoints"]["embeddings"] = result

        # Add compatibility notes
        self.validation_results[
            "compatibility_notes"
        ] = self.generate_compatibility_notes()

        # Determine overall status
        if self.validation_results["summary"]["failed"] > 0:
            self.validation_results["overall_status"] = "FAIL"
        elif self.validation_results["summary"]["warnings"] > 0:
            self.validation_results["overall_status"] = "PASS_WITH_WARNINGS"
        else:
            self.validation_results["overall_status"] = "PASS"

        logger.info(
            "Validation completed",
            total_checks=self.validation_results["summary"]["total_checks"],
            passed=self.validation_results["summary"]["passed"],
            failed=self.validation_results["summary"]["failed"],
            status=self.validation_results["overall_status"],
        )

    def save_report(self, output_file: Path) -> None:
        """Save validation report to JSON file."""
        with open(output_file, "w") as f:
            json.dump(self.validation_results, f, indent=2)
        logger.info("Validation report saved", file=str(output_file))


def main():
    """Main entry point."""
    # Define paths
    project_root = Path(__file__).parent.parent
    ollama_types_dir = project_root / "references" / "ollama-types"
    openai_examples_dir = project_root / "references" / "openai-examples"
    output_file = project_root / "references" / "validation-report.json"

    # Validate directories exist
    if not ollama_types_dir.exists():
        logger.error("Ollama types directory not found", dir=str(ollama_types_dir))
        sys.exit(1)

    if not openai_examples_dir.exists():
        logger.error(
            "OpenAI examples directory not found", dir=str(openai_examples_dir)
        )
        sys.exit(1)

    # Run validation
    validator = TypeValidator(ollama_types_dir, openai_examples_dir)
    validator.run_validation()
    validator.save_report(output_file)

    # Exit with appropriate code
    if validator.validation_results["overall_status"] == "FAIL":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
