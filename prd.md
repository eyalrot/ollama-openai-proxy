# Ollama-OpenAI Proxy Product Requirements Document (PRD)

## Goals and Background Context

### Goals

- Enable zero-code migration from Ollama SDK to OpenAI-compatible services
- Support core Ollama API endpoints (/api/tags, /api/generate, /api/chat, /api/embeddings)
- Provide transparent proxy service with minimal latency overhead (<50ms)
- Maintain streaming support for real-time applications
- Create drop-in replacement that preserves existing codebase investments
- Support multiple OpenAI-compatible providers (OpenAI, OpenRouter, LiteLLM)

### Background Context

Organizations using Ollama SDK face significant refactoring costs when migrating to OpenAI-compatible services. This proxy service solves the migration friction by providing a FastAPI server that receives HTTP/REST requests from Ollama SDK clients, translates them to OpenAI format using the OpenAI SDK, forwards them to OpenAI-compatible endpoints, and translates the responses back to Ollama format. The translation layer inside the FastAPI server handles all format conversions, parameter mappings, and streaming transformations. This enables teams to leverage more scalable or feature-rich LLM providers without modifying their existing applications.

The solution focuses on transparency and simplicity, following KISS and YAGNI principles to deliver only what's needed for successful migration while maintaining compatibility with the Ollama SDK's expected behavior.

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2024-01-26 | 1.0 | Initial PRD creation | Original Author |
| 2024-01-26 | 2.0 | Converted to BMad template format | Sarah (PO) |
| 2025-07-29 | 3.0 | Refactored to SDK-based TDD approach | Claude (PO) |
| 2025-07-29 | 3.1 | Swapped Epic 4 & 5 - Chat endpoint before Generate | Sarah (PO) |

## Requirements

### Functional

- FR1: The proxy service MUST listen on port 11434 (Ollama default) and accept HTTP requests in Ollama API format
- FR2: The `/api/tags` endpoint MUST return available OpenAI models formatted as Ollama model list with dummy metadata for missing fields
- FR3: The `/api/generate` endpoint MUST support both streaming and non-streaming text generation with parameter translation
- FR4: The `/api/chat` endpoint MUST handle conversational interactions with proper message role mapping
- FR5: The `/api/embeddings` endpoint MUST support batch embedding requests and format responses correctly
- FR6: All endpoints MUST translate Ollama-specific parameters to OpenAI equivalents where possible
- FR7: The service MUST log warnings for unmappable Ollama-specific parameters (e.g., top_k, repeat_last_n)
- FR8: Error responses from OpenAI MUST be translated to Ollama-compatible error formats
- FR9: The service MUST support configuration via environment variables for API keys and endpoints
- FR10: Streaming responses MUST maintain real-time delivery with minimal buffering
- FR11: The proxy MUST pass all Ollama SDK integration tests for supported endpoints
- FR12: The service MUST extract and use Pydantic models from official Ollama SDK source
- FR13: The service MUST collect and store real OpenAI API responses for test fixtures
- FR14: OpenAI API key MUST be required for development phase response collection
- FR15: Users MUST provide their own valid OpenAI API key via OPENAI_API_KEY environment variable for the proxy to function

### Non Functional

- NFR1: Proxy overhead latency MUST be less than 50ms excluding LLM response time
- NFR2: The service MUST support minimum 100 concurrent requests
- NFR3: Target uptime of 99.9% availability
- NFR4: Compatible with Ollama SDK latest stable version
- NFR5: Support Python 3.8+ runtime environments
- NFR6: Docker containerization for easy deployment
- NFR7: Structured JSON logging for debugging and monitoring
- NFR8: Configurable request timeouts with graceful error handling
- NFR9: No caching of responses in Phase 1
- NFR10: Single OpenAI endpoint configuration per proxy instance

## Technical Assumptions

### Repository Structure: Monorepo

Single repository containing all proxy service code, tests, and documentation.

### Service Architecture

**CRITICAL DECISION** - Monolithic proxy service with clear internal component separation:
- FastAPI server receiving Ollama SDK HTTP/REST requests
- Translation layer inside FastAPI for Ollama↔OpenAI format conversion
- OpenAI SDK client for communicating with OpenAI-compatible endpoints

### Testing Requirements

**CRITICAL DECISION** - Test-Driven Development (TDD) approach:
- Write tests BEFORE implementation using Ollama SDK as client
- Unit tests for all components (80% minimum coverage)
- Integration tests using actual Ollama SDK against our FastAPI server
- Test fixtures from real OpenAI API responses (stored in references/)
- OpenAI API key required for integration test execution
- No Ollama server used - we ARE the Ollama-compatible server

### Additional Technical Assumptions and Requests

- Python 3.12 as exact runtime version (per architecture document)
- FastAPI framework for async HTTP server implementation
- Pydantic for request/response validation and models
- OpenAI Python SDK for backend communication
- Docker and Docker Compose for containerization
- **Development Environment:** VSCode DevContainer pre-configured with Python 3.12, mounted at `/workspace`
- **DevContainer Status:** Already set up and ready - no build or configuration tasks needed
- **No Virtual Environment:** DevContainer eliminates venv management complexity
- GitHub Actions for CI/CD pipeline (running in Docker containers)
- Deployment target: On-premises Docker host
- No Kubernetes or cloud-specific services in Phase 1
- Environment-based configuration (no config files)
- Ollama SDK models extracted from GitHub source code
- Real OpenAI responses collected during development phase
- KISS principle enforcement - no premature optimization
- YAGNI principle - build only what stories specify
- Pydantic v2 features used throughout
- **Pre-commit hooks:** Can be temporarily disabled with `--no-verify` during development
- **Configuration Migration:** Environment variables can be updated without code changes. Future versions may introduce configuration versioning if needed

## High-Level Requirements for Product Owner

The following high-level requirements outline what needs to be delivered for the Ollama-OpenAI Proxy service. The Product Owner should define the epic breakdown and prioritization based on these requirements.

### Core Requirements

1. **SDK Type Extraction**: Extract and use Pydantic models from the official Ollama SDK source code to ensure 100% compatibility
2. **OpenAI Response Collection**: Collect real OpenAI API responses to use as test fixtures for accurate translation
3. **Test-Driven Development**: All endpoints must have integration tests written using Ollama SDK before implementation
4. **Model Listing** (/api/tags): Translate OpenAI model list to Ollama format
5. **Text Generation** (/api/generate): Support streaming and non-streaming text generation with parameter mapping
6. **Chat Completion** (/api/chat): Handle multi-turn conversations with role mapping
7. **Embeddings** (/api/embeddings): Support single and batch embedding requests
8. **Error Handling**: Comprehensive error translation between OpenAI and Ollama formats
9. **Streaming Support**: Real-time NDJSON streaming for generate and chat endpoints
10. **Documentation**: Auto-generated API docs, deployment guides, and troubleshooting information
11. **Code Quality Verification**: Final epic to ensure all coding standards are met and pre-commit hooks are working correctly

### Technical Constraints

- Must use Python 3.12 and FastAPI (pre-installed in DevContainer)
- Must extract types from Ollama SDK GitHub repository
- Must collect real OpenAI responses (requires API key)
- Integration tests must use actual Ollama SDK
- No Ollama server dependency - we ARE the server
- All models must use Pydantic v2 features
- Reference data stored in `references/` directory
- Development happens in pre-configured DevContainer at `/workspace`
- No virtual environment management needed (handled by container)
- No DevContainer setup tasks required - already configured with Python 3.12
- Pre-commit hooks can be skipped during rapid development
- Final delivery must pass all coding standards and hooks

## Epic Breakdown and Sequencing

### Epic Overview

The following epic structure provides a logical implementation sequence for the Ollama-OpenAI Proxy. Each epic builds upon the previous ones, following TDD principles and ensuring incremental value delivery.

### Epic 1: SDK Type Extraction & Response Collection
**Priority:** MUST DO FIRST  
**Duration:** 1-2 days  
**Purpose:** Extract Pydantic models from Ollama SDK and collect real OpenAI responses for accurate translation and testing.

**Deliverables:**
- Ollama SDK types extracted to `references/ollama-types/`
- OpenAI response examples collected in `references/openai-examples/`
- Extraction and collection scripts for future updates

### Epic 2: Core Infrastructure & Testing Framework
**Priority:** HIGH  
**Duration:** 2-3 days  
**Dependencies:** Epic 1  
**Purpose:** Establish FastAPI application foundation and testing framework using Ollama SDK as client.

**Deliverables:**
- FastAPI application structure
- Configuration management system
- Structured logging setup
- Test framework with Ollama SDK integration
- Health check endpoint

### Epic 3: Model Listing Endpoint (/api/tags)
**Priority:** HIGH  
**Duration:** 2 days  
**Dependencies:** Epic 2  
**Purpose:** Implement the simplest endpoint to prove the translation pattern works.

**Deliverables:**
- Working `/api/tags` endpoint
- Model translation logic (OpenAI → Ollama format)
- Integration tests with Ollama SDK

### Epic 4: Chat Endpoint (/api/chat)
**Priority:** HIGH  
**Duration:** 2-3 days  
**Dependencies:** Epic 2  
**Purpose:** Implement chat completion with message role mapping, conversation support, and streaming capabilities.

**Deliverables:**
- Working `/api/chat` endpoint
- Message role translation
- Multi-turn conversation support
- Streaming and non-streaming support

### Epic 5: Text Generation Endpoint (/api/generate)
**Priority:** HIGH  
**Duration:** 3-4 days  
**Dependencies:** Epic 2, benefits from Epic 4 streaming patterns  
**Purpose:** Implement text generation with streaming support and parameter mapping.

**Deliverables:**
- Working `/api/generate` endpoint
- Streaming and non-streaming support (reusing patterns from Epic 4)
- Parameter mapping and translation
- Warning logs for unsupported parameters

### Epic 6: Embeddings Endpoint (/api/embeddings)
**Priority:** MEDIUM  
**Duration:** 1-2 days  
**Dependencies:** Epic 2  
**Purpose:** Implement embeddings generation with batch support.

**Deliverables:**
- Working `/api/embeddings` endpoint
- Single and batch embedding support
- Proper response formatting

### Epic 7: Error Handling & Edge Cases
**Priority:** HIGH  
**Duration:** 2 days  
**Dependencies:** Epics 3-6  
**Purpose:** Consolidate error handling and address edge cases across all endpoints.

**Deliverables:**
- Comprehensive error translation
- Timeout handling
- Rate limit response handling
- Streaming error handling
- Request tracking for debugging

### Epic 8: Documentation & Deployment
**Priority:** MEDIUM  
**Duration:** 2 days  
**Dependencies:** Epic 7  
**Purpose:** Package the service for deployment with complete documentation.

**Deliverables:**
- API documentation (auto-generated and customized)
- Deployment guides
- Docker image and docker-compose
- Troubleshooting documentation

### Epic 9: Code Quality & Standards Verification
**Priority:** HIGH  
**Duration:** 1 day  
**Dependencies:** All previous epics  
**Purpose:** Final quality gate ensuring all standards are met before release.

**Deliverables:**
- All linting issues resolved
- 80%+ test coverage achieved
- Type checking passes
- Pre-commit hooks working
- Security scan completed

### Epic Dependencies and Sequencing

1. **Epic 1 MUST be completed first** - Without SDK types and OpenAI examples, accurate implementation is impossible
2. **Epic 2 MUST be second** - All endpoints require the core infrastructure
3. **Epics 3-6 can potentially run in parallel** after Epic 2, but recommended sequence:
   - Epic 3 first (simplest, validates approach)
   - Epic 4 next (chat with streaming, establishes patterns)
   - Epic 5 (generate endpoint, reuses Epic 4 streaming patterns)
   - Epic 6 (simplest, no streaming)
4. **Epic 7 consolidates after all endpoints** are complete
5. **Epics 8-9 finalize the project** for production readiness

**Note:** The Scrum Master will break down each epic into specific user stories during sprint planning.

## Checklist Results Report

### PO Master Checklist Validation Summary

**Date:** 2025-07-29  
**Validated By:** Sarah (Product Owner)  
**Checklist Used:** PO Master Validation Checklist  
**Project Type:** Greenfield (No UI)  
**Overall Readiness:** 100% (after addressing must-fix items)  

#### Issues Addressed

1. **FR15 Added** - Explicit requirement for users to provide OpenAI API key
2. **Epic Breakdown Added** - 9 epics with clear sequencing and dependencies
3. **Configuration Migration Added** - Note about environment variable updates

#### Final Validation Status

| Category | Status | Notes |
|----------|--------|-------|
| Project Setup & Initialization | ✅ PASS | DevContainer ready, clear process |
| Infrastructure & Deployment | ✅ PASS | Configuration migration addressed |
| External Dependencies | ✅ PASS | API key requirement explicit |
| User/Agent Responsibility | ✅ PASS | User API key provision clarified |
| Feature Sequencing | ✅ PASS | Epic breakdown with dependencies |
| MVP Scope Alignment | ✅ PASS | Clear scope, KISS/YAGNI enforced |
| Documentation & Handoff | ✅ PASS | Comprehensive planning |
| Post-MVP Considerations | ✅ PASS | Future enhancements considered |

**Decision:** APPROVED - The PRD is now comprehensive and ready for development.

## Next Steps

### UX Expert Prompt

Not applicable - This is a backend API proxy service with no user interface requirements.

### Architect Prompt

Please create a comprehensive architecture document for the Ollama-OpenAI Proxy service using this PRD as input. Focus on the technical implementation details, component design, and ensure alignment with the KISS/YAGNI principles outlined in the technical assumptions.