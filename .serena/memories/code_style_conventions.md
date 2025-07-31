# Code Style and Conventions

## Python Standards
- **Python Version**: 3.12 (exact version required)
- **Code Formatter**: black 23.12.1 (line length: 88)
- **Linter**: flake8 7.0.0
- **Type Checker**: mypy 1.8.0
- **Pre-commit hooks**: Can be temporarily disabled during rapid development

## Naming Conventions
- **Files**: snake_case (e.g., `request_translator.py`)
- **Classes**: PascalCase (e.g., `RequestTranslator`)
- **Functions**: snake_case (e.g., `translate_generate_request`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_RETRIES`)
- **Test files**: test_<module> (e.g., `test_request_translator.py`)

## Critical Coding Rules
- **Type hints required**: All functions must have complete type annotations
- **Async everywhere**: Use async/await for all I/O operations
- **No print statements**: Use structlog for all logging
- **Pydantic for validation**: Never manually validate JSON
- **No hardcoded values**: All configuration via environment variables
- **No commented code**: Delete unused code instead
- **Test coverage**: Minimum 80% coverage per component
- **Import order**: Standard library, third-party, local (separated by blank lines)
- **Docstrings**: Google style for all public functions
- **Exception handling**: Always catch specific exceptions
- **Context managers**: Use `async with` for all client operations