# Next Steps

## For Development Team

1. **Phase 0 - SDK Type Extraction & Response Collection** (First Story)
   - DevContainer with Python 3.12 is already set up - no build required
   - Clone Ollama SDK from GitHub
   - Run `scripts/extract_sdk_types.py` to extract Pydantic models
   - Set OPENAI_API_KEY environment variable
   - Run `scripts/collect_openai_responses.py` to gather test fixtures
   - Store extracted data in `references/` directory

2. **Phase 1 - TDD Implementation**
   - Write integration tests using Ollama SDK client first
   - Implement endpoints to make tests pass
   - Start with `/api/tags` endpoint
   - Validate against collected OpenAI responses
   - Each endpoint must have tests written before implementation

3. **Development Workflow**
   - All work happens in pre-configured DevContainer at `/workspace`
   - Python 3.12 environment is ready to use
   - Write tests first (TDD approach)
   - Run tests locally before committing
   - Pre-commit hooks can be skipped with `--no-verify` during development
   - Update architecture_learnings.md after each endpoint
   - Ensure OPENAI_API_KEY is set for integration tests
   - Final epic will verify all coding standards compliance

## For DevOps

1. Note: DevContainer is already configured with Python 3.12
2. Set up GitHub Actions workflow (use Docker containers)
3. Configure GitHub Secrets for OPENAI_API_KEY
4. Prepare Docker deployment scripts
5. Document deployment procedures

## Key Principles Reminder

- **KISS**: Always choose the simplest solution
- **YAGNI**: Build only what's needed for current story
- **Test Everything**: No code without tests
- **Document Learnings**: Update architecture_learnings.md continuously