#!/usr/bin/env python3
"""Collect real OpenAI API responses for translation testing.

This script collects responses from various OpenAI API endpoints to create
a comprehensive set of test fixtures for the Ollama-OpenAI proxy translator.
The collected responses help ensure accurate translation between OpenAI and
Ollama formats.

Cost Estimates (as of 2024):
- Models list: Free
- Chat completions (gpt-3.5-turbo): ~$0.002 per 1K tokens
- Chat completions (gpt-4): ~$0.03 per 1K tokens
- Total estimated cost for full collection: < $0.50

Usage:
    # Preview what will be collected (no API calls)
    python scripts/collect_openai_responses.py --dry-run

    # Collect all endpoints
    python scripts/collect_openai_responses.py

    # Collect specific endpoints only
    python scripts/collect_openai_responses.py --endpoints models chat
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog
from openai import AsyncOpenAI

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # dotenv not installed, proceed without it
    pass

logger = structlog.get_logger()

# Output directory for collected responses
OUTPUT_DIR = Path("references/openai-examples")


def setup_logging() -> None:
    """Configure structlog for the collection script."""
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


def check_api_key() -> str:
    """Check for OpenAI API key in environment.

    Returns:
        The API key from environment.

    Raises:
        SystemExit: If API key is not found.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.error(
            "OPENAI_API_KEY environment variable is required",
            hint="Set OPENAI_API_KEY in your .env file or export it",
        )
        sys.exit(1)

    # Mask the key for logging
    masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "***"
    logger.info("Found OpenAI API key", masked_key=masked_key)

    return api_key


def create_output_directories() -> None:
    """Create the output directory structure for responses."""
    directories = [
        OUTPUT_DIR,
        OUTPUT_DIR / "chat",
        OUTPUT_DIR / "completions",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {directory}")


def validate_json(data: Dict[str, Any]) -> bool:
    """Validate JSON structure of response.

    Args:
        data: The data to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        # Check required metadata fields
        if "metadata" not in data:
            logger.error("Missing metadata in response")
            return False

        metadata = data["metadata"]
        required_fields = ["endpoint", "timestamp"]
        for field in required_fields:
            if field not in metadata:
                logger.error(f"Missing required metadata field: {field}")
                return False

        # Check response exists
        if "response" not in data:
            logger.error("Missing response data")
            return False

        # Validate it can be serialized
        json.dumps(data)
        return True

    except Exception as e:
        logger.error(f"JSON validation failed: {e}")
        return False


def save_response(
    response_data: Dict[str, Any],
    endpoint: str,
    filename: str,
    request_params: Optional[Dict[str, Any]] = None,
) -> None:
    """Save API response with metadata.

    Args:
        response_data: The API response data
        endpoint: The API endpoint name
        filename: Output filename
        request_params: Request parameters used
    """
    # Determine output path
    if endpoint == "models":
        output_path = OUTPUT_DIR / filename
    elif endpoint == "chat":
        output_path = OUTPUT_DIR / "chat" / filename
    elif endpoint == "completions":
        output_path = OUTPUT_DIR / "completions" / filename
    else:
        output_path = OUTPUT_DIR / filename

    # Create metadata wrapper
    wrapped_response = {
        "metadata": {
            "endpoint": endpoint,
            "timestamp": datetime.utcnow().isoformat(),
            "request_params": request_params or {},
        },
        "response": response_data,
    }

    # Validate before saving
    if not validate_json(wrapped_response):
        logger.error(f"Skipping invalid response for {filename}")
        return

    # Save to file
    with open(output_path, "w") as f:
        json.dump(wrapped_response, f, indent=2)

    logger.info(f"Saved {endpoint} response", filename=str(output_path))


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Collect OpenAI API responses for testing"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be collected without making API calls",
    )
    parser.add_argument(
        "--endpoints",
        nargs="+",
        choices=["models", "chat", "completions", "all"],
        default=["all"],
        help="Which endpoints to collect from (default: all)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    return parser.parse_args()


def generate_index_file() -> None:
    """Generate an index file listing all collected examples."""
    logger.info("Generating index file")

    index_data = {
        "generated_at": datetime.utcnow().isoformat(),
        "endpoints": {},
        "total_files": 0,
        "summary": {},
    }

    # Scan for collected files
    for endpoint_dir in ["", "chat", "completions"]:
        dir_path = OUTPUT_DIR / endpoint_dir if endpoint_dir else OUTPUT_DIR
        if not dir_path.exists():
            continue

        # Find JSON files
        json_files = [f for f in dir_path.glob("*.json") if f.name != "index.json"]

        if not json_files:
            continue

        endpoint_name = endpoint_dir if endpoint_dir else "root"
        index_data["endpoints"][endpoint_name] = []

        for json_file in sorted(json_files):
            try:
                with open(json_file) as f:
                    data = json.load(f)

                file_info = {
                    "filename": json_file.name,
                    "path": str(json_file.relative_to(OUTPUT_DIR)),
                    "endpoint": data.get("metadata", {}).get("endpoint", "unknown"),
                    "timestamp": data.get("metadata", {}).get("timestamp", "unknown"),
                }

                # Extract key parameters
                params = data.get("metadata", {}).get("request_params", {})
                if params:
                    file_info["key_params"] = {
                        "model": params.get("model", "N/A"),
                        "temperature": params.get("temperature", "N/A"),
                        "stream": params.get("stream", False),
                    }

                index_data["endpoints"][endpoint_name].append(file_info)
                index_data["total_files"] += 1

            except Exception as e:
                logger.error(f"Failed to process {json_file}: {e}")

    # Generate summary statistics
    all_models = set()
    all_endpoints = set()

    for endpoint_files in index_data["endpoints"].values():
        for file_info in endpoint_files:
            all_endpoints.add(file_info["endpoint"])
            if "key_params" in file_info:
                model = file_info["key_params"].get("model")
                if model and model != "N/A":
                    all_models.add(model)

    index_data["summary"] = {
        "models_used": sorted(list(all_models)),
        "endpoints_covered": sorted(list(all_endpoints)),
        "parameter_variations": {
            "temperatures": "0.0, 0.3, 0.5, 0.7, 1.0",
            "includes_streaming": True,
            "includes_max_tokens": True,
        },
    }

    # Save index file
    index_path = OUTPUT_DIR / "index.json"
    with open(index_path, "w") as f:
        json.dump(index_data, f, indent=2)

    logger.info(f"Generated index with {index_data['total_files']} files")


class OpenAICollector:
    """Collector for OpenAI API responses."""

    def __init__(self, api_key: str, rate_limit_delay: float = 1.0):
        """Initialize the collector with OpenAI client.

        Args:
            api_key: OpenAI API key
            rate_limit_delay: Delay between API calls in seconds
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.rate_limit_delay = rate_limit_delay
        logger.info("Initialized OpenAI client", rate_limit_delay=rate_limit_delay)

    async def collect_models(self) -> Dict[str, Any]:
        """Collect response from models endpoint.

        Returns:
            The models list response
        """
        try:
            logger.info("Collecting models list")
            response = await self.client.models.list()

            # Convert to dict for JSON serialization
            models_data = {
                "object": "list",
                "data": [
                    {
                        "id": model.id,
                        "object": model.object,
                        "created": model.created,
                        "owned_by": model.owned_by,
                    }
                    for model in response.data
                ],
            }

            await asyncio.sleep(self.rate_limit_delay)
            return models_data

        except Exception as e:
            logger.error("Failed to collect models", error=str(e))
            raise

    async def collect_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        descriptor: str = "default",
    ) -> Dict[str, Any]:
        """Collect a chat completion response.

        Args:
            messages: List of message dicts with role and content
            model: Model to use
            temperature: Temperature for sampling
            max_tokens: Maximum tokens to generate
            stream: Whether to use streaming
            descriptor: Description for the example filename

        Returns:
            The chat completion response
        """
        try:
            logger.info(
                "Collecting chat completion",
                model=model,
                temperature=temperature,
                stream=stream,
                descriptor=descriptor,
            )

            params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
            }
            if max_tokens:
                params["max_tokens"] = max_tokens

            if stream:
                # Collect streaming response
                stream_response = await self.client.chat.completions.create(
                    **params, stream=True
                )

                chunks = []
                combined_content = ""
                async for chunk in stream_response:
                    chunk_dict = chunk.model_dump()
                    chunks.append(chunk_dict)

                    # Accumulate content
                    if chunk.choices and chunk.choices[0].delta.content:
                        combined_content += chunk.choices[0].delta.content

                # Return both individual chunks and combined response
                response_data = {
                    "stream": True,
                    "chunks": chunks,
                    "combined_content": combined_content,
                }
            else:
                # Collect non-streaming response
                response = await self.client.chat.completions.create(**params)
                response_data = response.model_dump()

            await asyncio.sleep(self.rate_limit_delay)
            return response_data

        except Exception as e:
            logger.error(
                "Failed to collect chat completion",
                model=model,
                descriptor=descriptor,
                error=str(e),
            )
            raise

    async def collect_chat_examples(self) -> None:
        """Collect various chat completion examples."""
        examples = [
            # Simple single-turn conversation
            {
                "descriptor": "simple_single_turn",
                "messages": [
                    {"role": "user", "content": "What is the capital of France?"}
                ],
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
            },
            # Multi-turn conversation with system prompt
            {
                "descriptor": "multi_turn_with_system",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "What is Python?"},
                    {
                        "role": "assistant",
                        "content": "Python is a high-level, interpreted programming "
                        + "language known for its simplicity and readability.",
                    },
                    {"role": "user", "content": "What are its main uses?"},
                ],
                "model": "gpt-3.5-turbo",
                "temperature": 0.5,
            },
            # Low temperature (deterministic)
            {
                "descriptor": "low_temperature",
                "messages": [
                    {"role": "user", "content": "List the first 5 prime numbers."}
                ],
                "model": "gpt-3.5-turbo",
                "temperature": 0.0,
            },
            # High temperature (creative)
            {
                "descriptor": "high_temperature",
                "messages": [
                    {
                        "role": "user",
                        "content": "Write a creative haiku about programming.",
                    }
                ],
                "model": "gpt-3.5-turbo",
                "temperature": 1.0,
            },
            # With max_tokens limit
            {
                "descriptor": "max_tokens_limit",
                "messages": [
                    {"role": "user", "content": "Explain quantum computing in detail."}
                ],
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 50,
            },
            # GPT-4 example (if available)
            {
                "descriptor": "gpt4_reasoning",
                "messages": [
                    {
                        "role": "user",
                        "content": "Solve this step by step: If a train travels "
                        + "120 miles in 2 hours, how far will it travel in 3.5 hours "
                        + "at the same speed?",
                    }
                ],
                "model": "gpt-4",
                "temperature": 0.3,
            },
        ]

        # Collect non-streaming examples
        for example in examples:
            try:
                response = await self.collect_chat_completion(
                    messages=example["messages"],
                    model=example.get("model", "gpt-3.5-turbo"),
                    temperature=example.get("temperature", 1.0),
                    max_tokens=example.get("max_tokens"),
                    stream=False,
                    descriptor=example["descriptor"],
                )

                filename = f"example_{example['descriptor']}.json"
                save_response(
                    response,
                    "chat",
                    filename,
                    request_params={
                        "messages": example["messages"],
                        "model": example.get("model", "gpt-3.5-turbo"),
                        "temperature": example.get("temperature", 1.0),
                        "max_tokens": example.get("max_tokens"),
                        "stream": False,
                    },
                )
            except Exception as e:
                logger.error(
                    f"Failed to collect {example['descriptor']}",
                    error=str(e),
                )
                # Continue with other examples

        # Collect streaming example
        try:
            streaming_example = {
                "messages": [{"role": "user", "content": "Count from 1 to 5 slowly."}],
                "model": "gpt-3.5-turbo",
                "temperature": 0.5,
            }

            response = await self.collect_chat_completion(
                messages=streaming_example["messages"],
                model=streaming_example["model"],
                temperature=streaming_example["temperature"],
                stream=True,
                descriptor="streaming",
            )

            save_response(
                response,
                "chat",
                "example_streaming.json",
                request_params={
                    **streaming_example,
                    "stream": True,
                },
            )
        except Exception as e:
            logger.error("Failed to collect streaming example", error=str(e))

    async def close(self) -> None:
        """Close the OpenAI client."""
        await self.client.close()


async def main() -> None:
    """Main entry point for the collection script."""
    args = parse_arguments()

    # Setup logging
    setup_logging()
    if args.verbose:
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        )

    logger.info("Starting OpenAI response collection", dry_run=args.dry_run)

    # Check for API key
    api_key = check_api_key()

    # Create output directories
    if not args.dry_run:
        create_output_directories()

    # Determine which endpoints to collect
    endpoints = args.endpoints
    if "all" in endpoints:
        endpoints = ["models", "chat", "completions"]

    logger.info("Collection plan", endpoints=endpoints)

    if args.dry_run:
        logger.info("Dry run mode - previewing collection plan")
        logger.info("Endpoints to collect:", endpoints=endpoints)
        if "chat" in endpoints:
            logger.info("Chat examples to collect: 7 (6 regular + 1 streaming)")
            logger.info("Estimated cost: < $0.20 for gpt-3.5-turbo examples")
            logger.info("Note: GPT-4 example may cost ~$0.10-0.30")
        logger.info("Total estimated cost: < $0.50")
        logger.info("Dry run complete - no API calls made")
        return

    # Initialize collector
    collector = OpenAICollector(api_key)

    try:
        # Collect from each endpoint
        if "models" in endpoints:
            models_response = await collector.collect_models()
            save_response(models_response, "models", "models.json")

        if "chat" in endpoints:
            await collector.collect_chat_examples()

        if "completions" in endpoints:
            logger.info(
                "Text completions endpoint is deprecated by OpenAI",
                note="Using chat completions API instead for all text generation",
            )
            # Create a placeholder file documenting the deprecation
            completions_note = {
                "metadata": {
                    "endpoint": "completions",
                    "timestamp": datetime.utcnow().isoformat(),
                    "note": "The legacy completions endpoint has been deprecated "
                    + "by OpenAI. All text generation should use the chat "
                    + "completions API instead.",
                },
                "migration_guide": {
                    "old_format": {
                        "endpoint": "/v1/completions",
                        "example": {
                            "model": "text-davinci-003",
                            "prompt": "Once upon a time",
                            "max_tokens": 50,
                        },
                    },
                    "new_format": {
                        "endpoint": "/v1/chat/completions",
                        "example": {
                            "model": "gpt-3.5-turbo",
                            "messages": [
                                {"role": "user", "content": "Once upon a time"},
                            ],
                            "max_tokens": 50,
                        },
                    },
                },
            }
            save_response(
                completions_note,
                "completions",
                "deprecation_notice.json",
            )

    except Exception as e:
        logger.error("Collection failed", error=str(e))
        sys.exit(1)

    finally:
        await collector.close()

    # Generate index file
    if not args.dry_run:
        generate_index_file()

    logger.info("Collection completed successfully")


if __name__ == "__main__":
    asyncio.run(main())
