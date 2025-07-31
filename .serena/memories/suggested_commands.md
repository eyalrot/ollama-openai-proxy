# Development Commands

## Essential Make Commands
- `make help` - Show all available commands
- `make setup` - Initial project setup (install dependencies, pre-commit hooks)
- `make run` - Run the proxy server on port 11434
- `make run-dev` - Run in development mode with auto-reload
- `make test` - Run all tests with coverage report
- `make test-unit` - Run unit tests only
- `make test-integration` - Run integration tests (requires OPENAI_API_KEY)
- `make format` - Format code with black
- `make lint` - Run flake8 linting checks  
- `make type-check` - Run mypy type checking
- `make quality` - Run all code quality checks (format, lint, type-check)
- `make coverage` - Generate test coverage report

## Development Workflow Commands
- `make extract-types` - Extract Pydantic models from Ollama SDK
- `make collect-responses` - Collect OpenAI API responses (requires OPENAI_API_KEY)
- `make validate-types` - Validate type compatibility between Ollama and OpenAI

## System Commands (Linux)
- `git status` - Check git status
- `git diff` - View uncommitted changes
- `git log` - View commit history
- `ls -la` - List files with details
- `find . -name "*.py"` - Find Python files
- `grep -r "pattern" .` - Search for patterns in files
- `cd /workspace` - Navigate to workspace root

## Server Commands
- Default server runs on: http://0.0.0.0:11434
- Health check endpoint: http://localhost:11434/health