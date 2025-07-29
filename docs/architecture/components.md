# Components

## SDK Type Extractor

**Responsibility:** Extract Pydantic models from Ollama SDK source code

**Key Interfaces:**
- `extract_models_from_sdk(sdk_path: str) -> Dict[str, str]`
- `save_raw_models(models: Dict[str, str], output_dir: str)`
- `analyze_model_fields(model_class: Type) -> Dict[str, Any]`

**Dependencies:** GitHub clone of Ollama SDK, Python AST parser

**Technology Stack:** Python 3.12, ast module, GitPython

**Notes:** Runs only during development phase, not part of runtime

## OpenAI Response Collector

**Responsibility:** Collect real OpenAI API responses for test fixtures

**Key Interfaces:**
- `collect_model_list() -> Dict[str, Any]`
- `collect_completion_examples(prompts: List[str]) -> List[Dict]`
- `collect_chat_examples(conversations: List[List[Dict]]) -> List[Dict]`
- `collect_embedding_examples(texts: List[str]) -> List[Dict]`
- `save_responses(responses: Dict[str, Any], output_dir: str)`

**Dependencies:** OpenAI SDK, Valid API key (required)

**Technology Stack:** OpenAI SDK 1.12.0, Python 3.12

**Notes:** Requires OPENAI_API_KEY environment variable

## FastAPI Server

**Responsibility:** HTTP server handling Ollama API endpoints and request routing

**Key Interfaces:**
- `GET /api/tags` - List available models
- `POST /api/generate` - Text generation (completion)
- `POST /api/chat` - Chat completion
- `POST /api/embeddings` - Generate embeddings
- `GET /health` - Health check endpoint
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation

**Dependencies:** Request Validator, Request/Response Translators, OpenAI Client Wrapper

**Technology Stack:** FastAPI 0.109.0, Uvicorn 0.27.0, Python 3.12

## Request Validator

**Responsibility:** Validate incoming Ollama requests using Pydantic models

**Key Interfaces:**
- `validate_generate_request(data: dict) -> OllamaGenerateRequest`
- `validate_chat_request(data: dict) -> OllamaChatRequest`
- `validate_embeddings_request(data: dict) -> OllamaEmbeddingsRequest`

**Dependencies:** Pydantic models based on extracted Ollama SDK types

**Technology Stack:** Pydantic 2.5.3

## Translation Layer

**Responsibility:** Convert between Ollama and OpenAI request/response formats

**Key Interfaces:**
- `translate_generate_request(ollama_req) -> OpenAICompletionRequest`
- `translate_chat_request(ollama_req) -> OpenAIChatRequest`
- `translate_embedding_request(ollama_req) -> OpenAIEmbeddingRequest`
- `translate_completion_response(openai_resp) -> OllamaGenerateResponse`
- `translate_chat_response(openai_resp) -> OllamaChatResponse`
- `translate_models_list(openai_models) -> OllamaTagsResponse`

**Dependencies:** Model Mapping configuration, Logging for unsupported parameters

**Technology Stack:** Pure Python with structlog for warning logs

## OpenAI Client Wrapper

**Responsibility:** Manage OpenAI API interactions with proper error handling

**Key Interfaces:**
- `list_models() -> List[Model]`
- `create_completion(**kwargs) -> CompletionResponse`
- `create_chat_completion(**kwargs) -> ChatResponse`
- `create_embedding(**kwargs) -> EmbeddingResponse`

**Dependencies:** OpenAI Python SDK, environment configuration

**Technology Stack:** OpenAI SDK 1.12.0, HTTPX 0.26.0

## Streaming Handler

**Responsibility:** Convert OpenAI SSE streaming format to Ollama's newline-delimited JSON format in real-time

**Key Interfaces:**
- `stream_generate_response(openai_stream) -> AsyncGenerator[str]`
- `stream_chat_response(openai_stream) -> AsyncGenerator[str]`
- `parse_sse_chunk(sse_data: str) -> dict` - Extract JSON from SSE format
- `format_ollama_chunk(openai_chunk: dict, done: bool) -> str` - Convert to NDJSON line
- `handle_stream_error(error: Exception) -> str` - Format streaming errors

**Dependencies:** JSON processing (orjson), Direct format conversion (no Response Translator)

**Technology Stack:** Python async generators, orjson 3.9.12, SSE parsing

**Streaming Format Details:**
- **Input:** OpenAI SSE format: `data: {"choices":[{"delta":{"content":"text"}}]}`
- **Output:** Ollama NDJSON format: `{"model":"...","response":"text","done":false}`
- **Completion Signal:** OpenAI sends `data: [DONE]`, convert to `{"done":true,...}`
- **Content Type:** Return `application/x-ndjson` with proper streaming headers

## Error Handler

**Responsibility:** Translate OpenAI errors to Ollama-compatible error format

**Key Interfaces:**
- `translate_openai_error(openai_error: OpenAIError) -> OllamaError`
- `get_error_status_code(error_type: str) -> int`

**Dependencies:** Error mapping configuration

**Technology Stack:** Pure Python exception handling
