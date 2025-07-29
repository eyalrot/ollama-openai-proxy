# Tech Stack

**CRITICAL**: This table represents the DEFINITIVE technology choices for the project. All implementation MUST use these exact versions and technologies.

## Cloud Infrastructure

- **Provider:** On-premises / Self-hosted
- **Key Services:** Docker host, GitHub (for CI/CD)
- **Deployment Regions:** N/A (on-premises)

## Technology Stack Table

| Category | Technology | Version | Purpose | Rationale |
|----------|------------|---------|---------|-----------|
| **Language** | Python | 3.12 | Primary development language | Required by dev environment spec, modern async support |
| **Runtime** | Python | 3.12 | Application runtime | Native async/await, performance improvements |
| **Framework** | FastAPI | 0.109.0 | Web framework | Native async, automatic OpenAPI docs, Pydantic integration |
| **ASGI Server** | Uvicorn | 0.27.0 | ASGI server | FastAPI recommended, production-ready, good performance |
| **Ollama SDK** | ollama | latest | Ollama client library | Source for type extraction, test client |
| **HTTP Client** | OpenAI SDK | 1.12.0 | OpenAI API client | Official SDK, streaming support, type safety |
| **HTTP Client** | HTTPX | 0.26.0 | Async HTTP client | Required by OpenAI SDK. Version pinned to 0.26.0 due to TestClient compatibility issues with httpx 0.27+ |
| **Validation** | Pydantic | 2.5.3 | Data validation | v2 features required, FastAPI integration, type safety |
| **JSON Processing** | orjson | 3.9.12 | Fast JSON parsing | 3x faster than standard json, recommended for performance |
| **Logging** | structlog | 24.1.0 | Structured logging | JSON output, context preservation, FastAPI integration |
| **Testing** | pytest | 7.4.4 | Test framework | Industry standard, async support, good fixture system |
| **Testing** | pytest-asyncio | 0.23.3 | Async test support | Required for testing async FastAPI endpoints |
| **Testing** | pytest-cov | 4.1.0 | Coverage reporting | Track test coverage, ensure quality |
| **Code Quality** | black | 23.12.1 | Code formatter | Consistent formatting, no debates |
| **Code Quality** | flake8 | 7.0.0 | Linter | Catch common errors, enforce style |
| **Code Quality** | mypy | 1.8.0 | Type checker | Catch type errors, improve code quality |
| **Container** | Docker | 24.0 | Containerization | Standard deployment, isolation, reproducibility |
| **Orchestration** | Docker Compose | 3.8 | Local orchestration | Simple multi-container management for development |
| **VCS** | Git | latest | Version control | Industry standard |
| **CI/CD** | GitHub Actions | N/A | CI/CD platform | Integrated with repository, free for public repos |
| **API Docs** | Swagger/ReDoc | Built-in | API documentation | Automatic from FastAPI, no additional setup |

**Please confirm these technology choices before proceeding. Are there any versions you'd like to adjust or additional tools to include?**

## Known Issues and Architectural Decisions

### Dependency Version Management
- **Decision:** All dependencies are pinned to specific versions to avoid compatibility issues
- **Rationale:** Breaking changes in dependencies can cause unexpected failures, especially in test environments
- **Example:** httpx 0.27+ introduced breaking changes that affected FastAPI's TestClient functionality

### Testing Infrastructure Limitations
- **Known Issue:** BaseHTTPMiddleware has known issues with exception handling in test environments
- **Impact:** One integration test (`test_generic_error_response`) is skipped due to this limitation
- **Workaround:** The test is marked with `@pytest.mark.skipif` with clear documentation
- **Note:** This only affects testing, not production code functionality

### Development Dependencies
- **httpx:** Version must remain at 0.26.0 for TestClient compatibility
- **Future Consideration:** When upgrading to newer FastAPI/Starlette versions, re-evaluate httpx compatibility
