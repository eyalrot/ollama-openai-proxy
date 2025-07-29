# Data Models

## Request/Response Models

**Purpose:** Validate and structure API requests/responses between Ollama SDK and the proxy

**Key Attributes:**
- All models extracted from Ollama SDK source code (GitHub)
- Stored as reference in `references/ollama-types/`
- Enhanced with Pydantic v2 features for our implementation
- Strict validation ensuring Ollama SDK compatibility
- Real OpenAI responses stored in `references/openai-examples/`

**Relationships:**
- OllamaRequest models → RequestTranslator → OpenAIRequest models
- OpenAIResponse models → ResponseTranslator → OllamaResponse models

## Model Mapping

**Purpose:** Define parameter and field mappings between Ollama and OpenAI APIs

**Key Attributes:**
- parameter_map: Dict[str, str] - Direct parameter mappings
- unsupported_params: List[str] - Parameters to log warnings for
- value_transformers: Dict[str, Callable] - Functions to transform parameter values

**Relationships:**
- Used by RequestTranslator and ResponseTranslator
- References both Ollama and OpenAI model definitions
