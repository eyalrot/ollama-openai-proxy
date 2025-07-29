# External APIs

## OpenAI API

- **Purpose:** Provides the actual AI model capabilities (completions, chat, embeddings)
- **Documentation:** https://platform.openai.com/docs/api-reference
- **Base URL(s):** https://api.openai.com/v1 (configurable via OPENAI_API_BASE_URL)
- **Authentication:** Bearer token using API key from environment variable
- **Rate Limits:** Depends on OpenAI account tier (not enforced by proxy in Phase 1)

**Key Endpoints Used:**
- `GET /models` - List available models
- `POST /completions` - Text generation
- `POST /chat/completions` - Chat-based generation
- `POST /embeddings` - Generate embeddings

**Integration Notes:** All requests include proper error handling with automatic retry (up to 3 attempts). Streaming responses use Server-Sent Events. API key must be valid or all requests will fail with 401.
