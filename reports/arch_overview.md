# Ollama-OpenAI Proxy Architecture Overview

## Project Goal Overview

This diagram illustrates the high-level goal of the Ollama-OpenAI Proxy - enabling applications using Ollama SDK to seamlessly connect to OpenAI-compatible services without code changes.

```mermaid
graph LR
    subgraph "Client Applications"
        A1[Application 1<br/>using Ollama SDK]
        A2[Application 2<br/>using Ollama SDK]
        A3[Application N<br/>using Ollama SDK]
    end
    
    subgraph "Ollama-OpenAI Proxy"
        P[FastAPI Server<br/>Port 11434]
    end
    
    subgraph "OpenAI-Compatible Services"
        O1[OpenAI API]
        O2[Azure OpenAI]
        O3[OpenRouter]
        O4[LiteLLM]
    end
    
    A1 -->|Ollama Protocol<br/>HTTP/REST| P
    A2 -->|Ollama Protocol<br/>HTTP/REST| P
    A3 -->|Ollama Protocol<br/>HTTP/REST| P
    
    P -->|OpenAI Protocol<br/>HTTPS| O1
    P -.->|Future Support| O2
    P -.->|Future Support| O3
    P -.->|Future Support| O4
    
    style A1 fill:#2196F3,stroke:#0D47A1,stroke-width:2px,color:#fff
    style A2 fill:#2196F3,stroke:#0D47A1,stroke-width:2px,color:#fff
    style A3 fill:#2196F3,stroke:#0D47A1,stroke-width:2px,color:#fff
    style P fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style O1 fill:#FF9800,stroke:#E65100,stroke-width:2px,color:#fff
    style O2 fill:#9E9E9E,stroke:#424242,stroke-width:1px,stroke-dasharray: 5 5,color:#fff
    style O3 fill:#9E9E9E,stroke:#424242,stroke-width:1px,stroke-dasharray: 5 5,color:#fff
    style O4 fill:#9E9E9E,stroke:#424242,stroke-width:1px,stroke-dasharray: 5 5,color:#fff
```

### Key Benefits:
- **Zero Code Changes**: Existing Ollama SDK applications work without modification
- **Drop-in Replacement**: Proxy runs on same port (11434) as Ollama
- **Protocol Translation**: Seamless conversion between Ollama and OpenAI formats
- **Future Extensibility**: Architecture supports multiple OpenAI-compatible providers

## Translation Layer Details

This diagram shows the internal translation layer and how requests/responses are transformed between Ollama and OpenAI protocols.

```mermaid
flowchart TB
    subgraph "Ollama SDK Client"
        OC[Ollama Client<br/>HTTP Request]
    end
    
    subgraph "Translation Layer Components"
        subgraph "Request Path"
            RV[Request Validator<br/>Pydantic Models]
            RT[Request Translator]
            PM[Parameter Mapper]
        end
        
        subgraph "Response Path"
            RST[Response Translator]
            EM[Error Mapper]
            SH[Streaming Handler<br/>SSE → NDJSON]
        end
    end
    
    subgraph "OpenAI Integration"
        OAI[OpenAI SDK Client]
        API[OpenAI API]
    end
    
    %% Request Flow
    OC -->|"/api/tags<br/>/api/generate<br/>/api/chat<br/>/api/embeddings"| RV
    RV -->|Validated<br/>Ollama Format| RT
    RT -->|Extract Parameters| PM
    PM -->|OpenAI Format| OAI
    OAI -->|HTTPS| API
    
    %% Response Flow
    API -->|Response| OAI
    OAI -->|Success Response| RST
    OAI -->|Error Response| EM
    OAI -->|Stream Response| SH
    
    RST -->|Ollama Format| OC
    EM -->|Ollama Error| OC
    SH -->|NDJSON Stream| OC
    
    %% Styling
    style OC fill:#2196F3,stroke:#0D47A1,stroke-width:2px,color:#fff
    style RV fill:#9C27B0,stroke:#4A148C,stroke-width:2px,color:#fff
    style RT fill:#9C27B0,stroke:#4A148C,stroke-width:2px,color:#fff
    style PM fill:#9C27B0,stroke:#4A148C,stroke-width:2px,color:#fff
    style RST fill:#4CAF50,stroke:#1B5E20,stroke-width:2px,color:#fff
    style EM fill:#F44336,stroke:#B71C1C,stroke-width:2px,color:#fff
    style SH fill:#03A9F4,stroke:#01579B,stroke-width:2px,color:#fff
    style OAI fill:#FF9800,stroke:#E65100,stroke-width:2px,color:#fff
    style API fill:#FF9800,stroke:#E65100,stroke-width:2px,color:#fff
```

### Translation Examples:

#### 1. Model Listing (`/api/tags`)
- **Ollama Request**: `GET /api/tags`
- **OpenAI Request**: `GET /v1/models`
- **Translation**: 
  - OpenAI model IDs → Ollama model names
  - Add required Ollama metadata fields (size, digest, etc.)
  - Format as Ollama tags response

#### 2. Text Generation (`/api/generate`)
- **Ollama Request**: 
  ```json
  {
    "model": "llama2",
    "prompt": "Hello",
    "stream": true,
    "options": {
      "temperature": 0.7,
      "top_k": 40
    }
  }
  ```
- **OpenAI Request**:
  ```json
  {
    "model": "gpt-3.5-turbo-instruct",
    "prompt": "Hello",
    "stream": true,
    "temperature": 0.7,
    "max_tokens": null
  }
  ```
- **Translation**:
  - Map model names
  - Convert Ollama options to OpenAI parameters
  - Log warnings for unsupported parameters (top_k)
  - Transform SSE stream to NDJSON

#### 3. Chat Completion (`/api/chat`)
- **Ollama Format**: Messages with role-based history
- **OpenAI Format**: Chat completion with messages array
- **Translation**: Direct message format mapping with role preservation

#### 4. Embeddings (`/api/embeddings`)
- **Ollama Format**: Single or batch text input
- **OpenAI Format**: Input array with model specification
- **Translation**: Format response with Ollama's expected embedding structure

### Streaming Translation

The streaming handler performs real-time format conversion:

```
OpenAI SSE Format:          Ollama NDJSON Format:
data: {"choices":[{...}]}   {"model":"...","response":"...","done":false}
data: {"choices":[{...}]}   {"model":"...","response":"...","done":false}
data: [DONE]                {"model":"...","response":"","done":true,"context":[...]}
```

### Error Translation

All OpenAI errors are mapped to Ollama-compatible error responses:
- HTTP status codes preserved
- Error messages reformatted
- Ollama-specific error structure maintained