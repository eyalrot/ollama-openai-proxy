# Ollama-OpenAI Proxy Project Overview

## Purpose
This project is a FastAPI-based proxy service that enables zero-code migration from Ollama SDK to OpenAI-compatible services. It acts as a transparent translation layer, receiving requests in Ollama API format and converting them to OpenAI format using the OpenAI SDK.

## Key Goals
- Enable seamless migration without modifying existing Ollama SDK client code
- Support core Ollama endpoints: /api/tags, /api/generate, /api/chat, /api/embeddings
- Provide minimal latency overhead (<50ms)
- Maintain streaming support for real-time applications
- Support multiple OpenAI-compatible providers

## Tech Stack
- **Language**: Python 3.12 (exact version required)
- **Framework**: FastAPI 0.109.0
- **Server**: Uvicorn 0.27.0
- **HTTP Client**: httpx 0.26.0
- **OpenAI SDK**: openai 1.12.0
- **Data Validation**: Pydantic 2.9+
- **Logging**: structlog 24.1.0
- **Serialization**: orjson 3.9.12
- **Development**: Running in DevContainer at /workspace

## Development Approach
- Test-Driven Development (TDD) methodology
- SDK-based type extraction from official Ollama SDK
- Real OpenAI API response collection for test fixtures
- Following KISS and YAGNI principles