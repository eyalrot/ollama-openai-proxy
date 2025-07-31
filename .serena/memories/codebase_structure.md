# Codebase Structure

## Root Directory
- `/workspace` - DevContainer root directory
- Key config files: `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, `Makefile`, `pytest.ini`, `mypy.ini`, `.flake8`

## Main Application (`/app`)
- `main.py` - FastAPI application entry point
- `config.py` - Environment configuration using Pydantic Settings
- `__init__.py` - Contains version information

### Application Subdirectories
- `/app/models/` - Data models
  - `/ollama/` - Ollama API models (extracted from SDK)
  - `/openai/` - OpenAI API models
- `/app/translators/` - Request/response translation logic
- `/app/handlers/` - API endpoint handlers (generate, chat, embeddings, tags, health)
- `/app/clients/` - OpenAI SDK wrapper
- `/app/utils/` - Utilities (streaming, errors, logging, middleware)

## Testing (`/tests`)
- `/tests/unit/` - Component-level tests
- `/tests/integration/` - Ollama SDK integration tests
- `conftest.py` - Pytest configuration

## Scripts (`/scripts`)
- Development automation scripts
- SDK type extraction and response collection

## References (`/references`)
- `/ollama-types/` - Extracted Ollama SDK models
- `/openai-examples/` - Collected OpenAI API responses
- Note: Not included in production deployment

## Documentation (`/docs`)
- `/architecture/` - Sharded architecture documentation
- `/stories/` - User story documentation
- `/templates/` - Document templates
- `prd.md` - Product Requirements Document

## BMAD Method (`/.bmad-core`)
- Contains BMAD methodology documentation and checklists
- Agent definitions and task templates

## Current Implementation Status
- Basic FastAPI setup completed
- Logging and error handling infrastructure in place
- Health check endpoint implemented
- Ready for endpoint implementation