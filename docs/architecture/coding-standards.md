# Coding Standards

## Core Standards

- **Languages & Runtimes:** Python 3.12 (exact version required)
- **Style & Linting:** black (23.12.1), flake8 (7.0.0), mypy (1.8.0)
- **Pre-commit Hooks:** Can be temporarily disabled during rapid development
  - Use `git commit --no-verify` when needed
  - Epic planned to ensure all hooks are working before final delivery
- **Test Organization:** `tests/unit/test_<component>.py`, `tests/integration/test_<endpoint>_integration.py`

## Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Files | snake_case | `request_translator.py` |
| Classes | PascalCase | `RequestTranslator` |
| Functions | snake_case | `translate_generate_request` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRIES` |
| Test files | test_<module> | `test_request_translator.py` |

## Critical Rules

- **DevContainer Usage:** All development happens inside the DevContainer at `/workspace`
- **No venv Management:** DevContainer eliminates need for virtual environment activation
- **No console.log:** Use structlog for all logging, never print statements
- **Use type hints:** All functions must have complete type annotations
- **Test coverage:** Minimum 80% coverage per component
- **No hardcoded values:** All configuration via environment variables
- **Pydantic for validation:** Never manually validate JSON, use Pydantic models
- **Async everywhere:** Use async/await for all I/O operations
- **No commented code:** Delete unused code, don't comment it out
- **Coding Standards Epic:** Final epic will verify all coding standards and pre-commit hooks

## Language-Specific Guidelines

### Python Specifics

- **Import order:** Standard library, third-party, local (separated by blank lines)
- **Docstrings:** Use Google style docstrings for all public functions
- **Exception handling:** Always catch specific exceptions, never bare except
- **Context managers:** Use `async with` for all client operations
