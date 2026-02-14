---
name: gemini-api
description: |
  Google Gemini API - Google's most intelligent multimodal AI model for generation, reasoning, and tool use.
  
  Use when:
  - Need text generation with multimodal understanding (images, video, audio, PDF)
  - Need structured JSON output for automated processing
  - Building agentic workflows with function calling
  - Voice applications with Live API
  - Image/video generation with Veo and Nano Banana
  - Long context processing (millions of tokens)
  - Code execution and computer use
  
  Supported models: Gemini 3, Gemini 2.5 Flash, Gemini 2.5 Pro, Veo (video), Nano Banana (image)
metadata:
  {
    "openclaw":
      {
        "requires": { "env": ["GEMINI_API_KEY"] },
      },
  }
---

# Gemini API

Google's most intelligent multimodal AI model API. The fastest path from prompt to production.

## Quick Start

### Python

```python
from google import genai

client = genai.Client(api_key="YOUR_API_KEY")
response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents="Explain how AI works in a few words"
)
print(response.text)
```

### JavaScript/TypeScript

```typescript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({ apiKey: "YOUR_API_KEY" });
const response = await ai.models.generateContent({
    model: "gemini-2.0-flash-001",
    contents: "Explain how AI works in a few words"
});
console.log(response.text);
```

### cURL

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-001:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H 'Content-Type: application/json' \
  -X POST \
  -d '{"contents": [{"parts": [{"text": "Explain how AI works in a few words"}]}]}'
```

## Available Models

| Model | Description | Use Case |
|-------|-------------|----------|
| gemini-2.5-pro | Most intelligent, frontier-level reasoning | Complex reasoning, multimodal understanding |
| gemini-2.5-flash | Fast, cost-effective, thinking included | Balanced performance and speed |
| gemini-2.0-flash-001 | Fast generation | High-volume applications |
| gemini-1.5-pro | Long context (2M tokens) | Large document processing |
| gemini-1.5-flash | Fast, affordable | General purpose |
| gemini-2.0-flash-exp | Experimental features | Testing new capabilities |
| imagen-3.0-generate-002 | Image generation | Create images from text |
| imagen-3.0-fast-generate-002 | Fast image generation | Quick image creation |
| gemini-2.0-flash-live-001 | Real-time voice | Live voice applications |
| veo-3.0-generate-001 | Video generation | Create videos from text/image |

## Key Features

### Multimodal Understanding
Process images, video, audio, PDF, and documents with full understanding. Support for up to 1M tokens.

### JSON Mode
Constrain Gemini to respond with JSON for automated processing:

```python
response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents="Extract user info from this text",
    config={
        "response_mime_type": "application/json",
        "response_schema": {"type": "OBJECT", "properties": {"name": {"type": "STRING"}}}
    }
)
```

### Function Calling (Tools)
Connect Gemini to external APIs and tools:

```python
from google.genai import types

tools = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="get_weather",
            description="Get weather for a location",
            parameters={"type": "OBJECT", "properties": {"location": {"type": "STRING"}}}
        )
    ]
)

response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents="What's the weather in Tokyo?",
    config=types.GenerateContentConfig(tools=[tools])
)
```

### Thinking/Reasoning
Enable thinking capabilities for complex reasoning:

```python
response = client.models.generate_content(
    model="gemini-2.5-flash-preview-05-20",
    contents="Solve this complex problem",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=1024)
    )
)
```

### Live API (Real-time Voice)
Build real-time voice applications:

```python
# See Live API documentation for full implementation
```

### Code Execution
Execute code directly:

```python
response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents="Calculate fibonacci(100)",
    config=types.GenerateContentConfig(
        tools=[types.Tool(code_execution=types.ToolCodeExecution())]
    )
)
```

## API Parameter Reference

| Parameter | Type | Description |
|-----------|------|-------------|
| model | string | Model name (required) |
| contents | list | Input content (required) |
| system_instruction | string | System prompt |
| temperature | float | Creativity (0.0-2.0) |
| max_output_tokens | int | Max response tokens |
| top_p | float | Nucleus sampling |
| top_k | int | Top-k sampling |
| response_mime_type | string | Output format (text/json) |
| response_schema | object | JSON schema for structured output |
| tools | list | Function declarations |
| safety_settings | list | Content filtering |
| thinking_config | object | Thinking budget settings |

## Environment Setup

```bash
# Set API key
export GEMINI_API_KEY="your-api-key"

# Or use .env file
echo "GEMINI_API_KEY=your-api-key" > .env
```

## Installation

```bash
pip install google-genai
# or
npm install @google/genai
```

## Use Cases

1. **Text Generation**: Q&A, content creation, summarization
2. **Image Analysis**: Extract info from images, charts, diagrams
3. **Document Processing**: PDF parsing, text extraction
4. **Video Understanding**: Analyze video content
5. **Code Generation**: Write, debug, explain code
6. **Agentic Workflows**: Connect to external tools via function calling
7. **Voice Applications**: Real-time voice with Live API
8. **Image Generation**: Create images with Nano Banana
9. **Video Generation**: Create videos with Veo

## Official Resources

- [Documentation](https://ai.google.dev/gemini-api/docs)
- [API Reference](https://ai.google.dev/docs)
- [Quickstart](https://ai.google.dev/docs/gemini-api/quickstart)
- [Model Versions](https://ai.google.dev/docs/gemini-api/model-versioning)
- [Pricing](https://ai.google.dev/pricing)
- [Status](https://status.google/)
