# Error Handling Strategy

## General Approach

- **Error Model:** Exception-based with specific error types for each failure mode
- **Exception Hierarchy:** Base `ProxyError` with specific subclasses for translation, client, and validation errors
- **Error Propagation:** Catch at handler level, translate to appropriate HTTP response

## Logging Standards

- **Library:** structlog 24.1.0
- **Format:** JSON structured logs
- **Levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Required Context:**
  - Correlation ID: UUID per request
  - Service Context: Component name, method name
  - User Context: No user tracking in Phase 1

## Error Handling Patterns

### External API Errors

- **Retry Policy:** Built-in OpenAI SDK retry with max_retries=3
- **Circuit Breaker:** Not implemented in Phase 1 (YAGNI)
- **Timeout Configuration:** 600 seconds (configurable via REQUEST_TIMEOUT)
- **Error Translation:** Direct mapping of OpenAI errors to Ollama format

### Streaming-Specific Error Handling

- **Mid-Stream Errors:** Convert to error NDJSON line with `"error"` field
- **Connection Drops:** Gracefully close stream with final `{"done":true,"error":"connection lost"}`
- **Format:** `{"error":"error message","done":true}` for streaming errors
- **Partial Response Handling:** Include any partial content before error occurs

### Business Logic Errors

- **Custom Exceptions:** `ValidationError`, `TranslationError`, `UnsupportedParameterError`, `StreamingError`
- **User-Facing Errors:** JSON error response matching Ollama format
- **Error Codes:** Use HTTP status codes only

### Data Consistency

- **Transaction Strategy:** N/A - stateless service
- **Compensation Logic:** N/A - no state to compensate
- **Idempotency:** All operations are naturally idempotent
