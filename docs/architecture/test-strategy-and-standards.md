# Test Strategy and Standards

## Testing Philosophy

- **Approach:** Test-Driven Development (TDD) - Write tests first using Ollama SDK
- **Coverage Goals:** 80% minimum per component, 90% for critical paths
- **Test Pyramid:** 70% unit tests, 25% integration tests, 5% e2e tests
- **OpenAI API Key:** Required for integration tests and response collection

## Test Types and Organization

### Unit Tests

- **Framework:** pytest 7.4.4
- **File Convention:** `test_<module_name>.py`
- **Location:** `tests/unit/`
- **Mocking Library:** pytest built-in fixtures and unittest.mock
- **Coverage Requirement:** 80% minimum

**AI Agent Requirements:**
- Generate tests for all public methods
- Cover edge cases and error conditions
- Follow AAA pattern (Arrange, Act, Assert)
- Mock all external dependencies

### Integration Tests

- **Scope:** Test with actual Ollama SDK against running proxy
- **Location:** `tests/integration/`
- **Test Infrastructure:**
  - **OpenAI API:** Mock using collected responses from `references/openai-examples/`
  - **Ollama SDK:** Real SDK configured to hit localhost:11434
  - **FastAPI Server:** Running instance of our proxy
- **OpenAI API Key:** Required for collecting test fixtures

### End-to-End Tests

- **Framework:** pytest with real services
- **Scope:** Full request/response flow with actual OpenAI API (Phase 2)
- **Environment:** Local Docker environment
- **Test Data:** Minimal prompts to reduce API costs

## Test Data Management

- **Strategy:** Real responses collected from OpenAI API
- **Fixtures:** `references/openai-examples/` containing actual API responses
- **SDK Types:** `references/ollama-types/` for validation
- **Factories:** Not needed for this simple proxy
- **Cleanup:** No cleanup needed (stateless service)

## Continuous Testing

- **CI Integration:** GitHub Actions runs all tests on PR
- **Performance Tests:** Not in Phase 1 scope
- **Security Tests:** Dependency scanning only

## Known Testing Limitations

### Middleware Exception Handling
- **Issue:** BaseHTTPMiddleware in Starlette has known issues with exception handling in TestClient
- **Impact:** Generic exception handler tests may fail due to ExceptionGroup wrapping
- **Affected Tests:** `test_generic_error_response` in integration tests
- **Resolution:** Tests are marked with `@pytest.mark.skipif` with documentation
- **Note:** This limitation only affects test environments, not production functionality

### Dependency Compatibility
- **httpx Version:** Must use 0.26.0 for TestClient compatibility
- **Breaking Changes:** httpx 0.27+ introduces incompatible changes with FastAPI's TestClient
- **Lesson Learned:** Pin all test dependencies to specific versions to avoid compatibility issues
