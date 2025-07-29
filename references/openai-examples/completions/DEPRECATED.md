# Text Completions Endpoint - DEPRECATED

The OpenAI text completions endpoint (`/v1/completions`) has been deprecated in favor of the chat completions endpoint.

## Migration Notice
- All text completion models have been discontinued
- Use the chat completions endpoint instead
- For instruction-following tasks, use `gpt-3.5-turbo-instruct` via the chat completions endpoint

## Historical Reference
The text completions endpoint accepted requests in this format:
```json
{
  "model": "text-davinci-003",
  "prompt": "Once upon a time",
  "max_tokens": 100,
  "temperature": 0.7
}
```

And returned responses like:
```json
{
  "id": "cmpl-xxx",
  "object": "text_completion",
  "created": 1589478378,
  "model": "text-davinci-003",
  "choices": [
    {
      "text": " there was a young princess who lived in a beautiful castle...",
      "index": 0,
      "logprobs": null,
      "finish_reason": "length"
    }
  ],
  "usage": {
    "prompt_tokens": 5,
    "completion_tokens": 100,
    "total_tokens": 105
  }
}
```

For the Ollama-OpenAI proxy project, we will not need to support this deprecated endpoint.