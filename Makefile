.PHONY: help
help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: extract-types
extract-types:  ## Extract Pydantic models from Ollama SDK
	python3 scripts/extract_sdk_types.py

.PHONY: collect-responses
collect-responses:  ## Collect OpenAI API responses (requires OPENAI_API_KEY)
	@if [ -z "$$OPENAI_API_KEY" ]; then \
		echo "Error: OPENAI_API_KEY environment variable is not set"; \
		echo "Please set it in your .env file or export it"; \
		exit 1; \
	fi
	python3 scripts/collect_openai_responses.py

.PHONY: setup
setup:  ## Initial project setup
	pip install -r requirements-dev.txt
	pre-commit install

.PHONY: validate-types
validate-types:  ## Validate type compatibility between Ollama and OpenAI
	python3 scripts/validate_type_compatibility.py

.PHONY: test
test:  ## Run all tests
	pytest -v --cov=app --cov-report=term-missing --cov-report=html --cov-fail-under=80

.PHONY: test-unit
test-unit:  ## Run unit tests only
	pytest -v -m unit tests/unit/

.PHONY: test-integration
test-integration:  ## Run integration tests only
	pytest -v -m integration tests/integration/

.PHONY: coverage
coverage:  ## Generate test coverage report
	pytest --cov=app --cov-report=term-missing --cov-report=html --cov-fail-under=80

.PHONY: run
run:  ## Run the proxy server
	uvicorn app.main:app --host 0.0.0.0 --port 11434

.PHONY: run-dev
run-dev:  ## Run in development mode with auto-reload
	uvicorn app.main:app --host 0.0.0.0 --port 11434 --reload

.PHONY: format
format:  ## Format code with black
	black app/ tests/ scripts/

.PHONY: lint
lint:  ## Run linting checks
	flake8 app/ tests/ scripts/

.PHONY: type-check
type-check:  ## Run type checking with mypy
	mypy app/

.PHONY: quality
quality: format lint type-check  ## Run all code quality checks