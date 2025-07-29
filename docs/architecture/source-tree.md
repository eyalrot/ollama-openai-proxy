# Source Tree

```plaintext
ollama-openai-proxy/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Environment configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── ollama/               # Ollama API models (SDK-based)
│   │   │   ├── __init__.py
│   │   │   ├── generate.py
│   │   │   ├── chat.py
│   │   │   ├── embeddings.py
│   │   │   └── models.py
│   │   └── openai/               # OpenAI API models
│   │       ├── __init__.py
│   │       └── models.py
│   ├── translators/
│   │   ├── __init__.py
│   │   ├── request.py            # Request translation logic
│   │   ├── response.py           # Response translation logic
│   │   └── mappings.py           # Parameter mapping definitions
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── generate.py           # /api/generate endpoint
│   │   ├── chat.py               # /api/chat endpoint
│   │   ├── embeddings.py         # /api/embeddings endpoint
│   │   ├── tags.py               # /api/tags endpoint
│   │   └── health.py             # /health endpoint
│   ├── clients/
│   │   ├── __init__.py
│   │   └── openai_client.py      # OpenAI SDK wrapper
│   └── utils/
│       ├── __init__.py
│       ├── streaming.py          # Streaming utilities
│       ├── errors.py             # Error handling
│       └── logging.py            # Logging configuration
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Pytest configuration
│   ├── integration/              # Ollama SDK tests
│   │   ├── __init__.py
│   │   ├── test_tags_integration.py
│   │   ├── test_generate_integration.py
│   │   ├── test_chat_integration.py
│   │   └── test_embeddings_integration.py
│   └── unit/                     # Component tests
│       ├── __init__.py
│       ├── test_request_translator.py
│       ├── test_response_translator.py
│       ├── test_parameter_mapping.py
│       ├── test_error_handling.py
│       └── test_streaming_handler.py
├── scripts/
│   ├── setup_dev.sh              # Development environment setup
│   ├── extract_sdk_types.py      # Extract types from Ollama SDK
│   ├── collect_openai_responses.py # Collect OpenAI responses
│   ├── run_tests.sh              # Run all tests
│   └── run_local.sh              # Run proxy locally
├── references/                   # Reference data (not in production)
│   ├── ollama-types/            # Raw extracted Ollama SDK models
│   │   ├── __init__.py
│   │   ├── generate.py
│   │   ├── chat.py
│   │   ├── embeddings.py
│   │   └── models.py
│   └── openai-examples/         # Collected OpenAI responses
│       ├── models.json
│       ├── completions/
│       │   └── example_*.json
│       ├── chat/
│       │   └── example_*.json
│       └── embeddings/
│           └── example_*.json
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── docs/
│   ├── architecture.md           # This document
│   ├── architecture_learnings.md # Learnings from implementation
│   └── prd.md                   # Product Requirements Document
├── .env.example                  # Example configuration
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
├── pytest.ini                    # Pytest configuration
├── .gitignore
├── Makefile                      # User-friendly commands (see below)
└── README.md                     # Project overview
```

## Directory Structure Notes

**Validation:** This directory structure has been reviewed and validated for the project needs:

1. **Clear separation of concerns** - Each component has its own module
2. **Test organization** - Separate unit and integration test directories
3. **Reference data isolation** - Non-production data clearly separated
4. **Script organization** - All automation scripts in one location
5. **Documentation centralization** - All docs in the docs/ folder

**Key Points:**
- The `app/` directory contains all production code
- The `references/` directory is for development only (not deployed)
- Scripts should be executable and have clear names
- All Python packages must have `__init__.py` files
- Test files follow the `test_*.py` naming convention

## Makefile Requirements

**Purpose:** Provide user-friendly commands for common development tasks.

**Key Principle:** The Makefile MUST be created during Epic 1 and updated after EACH story completion to include new capabilities.

**Initial Makefile targets (Epic 1):**
```makefile
.PHONY: help
help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: extract-types
extract-types:  ## Extract Pydantic models from Ollama SDK
	python scripts/extract_sdk_types.py

.PHONY: collect-responses
collect-responses:  ## Collect OpenAI API responses (requires OPENAI_API_KEY)
	python scripts/collect_openai_responses.py

.PHONY: setup
setup:  ## Initial project setup
	pip install -r requirements-dev.txt
	pre-commit install
```

**Progressive Makefile expansion per Epic:**

- **Epic 2:** Add `test`, `test-unit`, `test-integration`, `lint`, `format`, `type-check`
- **Epic 3:** Add `run`, `run-dev`, `test-tags`
- **Epic 4:** Add `test-generate`, `test-streaming`
- **Epic 5:** Add `test-chat`
- **Epic 6:** Add `test-embeddings`
- **Epic 7:** Add `test-all`, `coverage`
- **Epic 8:** Add `build`, `docker-build`, `docker-run`, `docs`
- **Epic 9:** Add `validate`, `pre-commit`, `clean`

**Example expanded Makefile (by Epic 3):**
```makefile
.PHONY: run
run:  ## Run the proxy server
	uvicorn app.main:app --host 0.0.0.0 --port 11434

.PHONY: run-dev
run-dev:  ## Run in development mode with auto-reload
	uvicorn app.main:app --host 0.0.0.0 --port 11434 --reload

.PHONY: test
test:  ## Run all tests
	pytest -v

.PHONY: test-unit
test-unit:  ## Run unit tests only
	pytest -v tests/unit/

.PHONY: test-integration
test-integration:  ## Run integration tests (requires OPENAI_API_KEY)
	pytest -v tests/integration/

.PHONY: lint
lint:  ## Run linting checks
	flake8 app/ tests/
	mypy app/

.PHONY: format
format:  ## Format code with black
	black app/ tests/
```

**Makefile Guidelines:**
1. Each target must have a help description
2. Use `.PHONY` for all non-file targets
3. Group related commands together
4. Add new targets immediately when new functionality is implemented
5. Include clear error messages for missing dependencies
6. Document environment variable requirements
