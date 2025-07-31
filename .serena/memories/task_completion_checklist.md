# Task Completion Checklist

When completing any development task, follow these steps:

## 1. Code Quality Checks
- Run `make format` to format code with black
- Run `make lint` to check flake8 compliance
- Run `make type-check` to verify mypy type annotations
- Or run `make quality` to run all three at once

## 2. Testing
- Run `make test` to execute all tests with coverage
- Ensure minimum 80% test coverage per component
- Run `make test-unit` for quick unit test validation
- Run `make test-integration` if changes affect API endpoints

## 3. Pre-commit Validation
- If pre-commit hooks are enabled, they will run automatically
- Can use `git commit --no-verify` during rapid development
- Final epic will ensure all hooks are working properly

## 4. Documentation
- Update relevant documentation if APIs change
- Ensure docstrings are present for public functions
- Update Makefile if new commands are added

## 5. Error Handling
- Verify all exceptions are specific (no bare except)
- Check that error responses follow Ollama format
- Ensure proper logging with structlog

## Important Notes
- Never use print statements - always use structlog
- All async operations should use proper context managers
- Environment variables should be used for all configuration
- DevContainer eliminates need for venv management