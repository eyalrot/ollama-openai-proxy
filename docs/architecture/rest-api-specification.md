# REST API Specification

**Note:** The exact REST API specification will be discovered during Epic 1 (SDK Type Extraction) by analyzing the Ollama SDK source code. This ensures 100% compatibility with the expected request and response structures.

During the SDK extraction phase, we will:
1. Extract all Pydantic models from the Ollama SDK
2. Document the exact request/response formats for each endpoint
3. Identify all required and optional parameters
4. Map parameter names and types between Ollama and OpenAI formats

This approach follows the TDD principle and ensures our implementation matches exactly what the Ollama SDK expects.
