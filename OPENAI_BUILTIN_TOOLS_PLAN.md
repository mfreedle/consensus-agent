# OpenAI Built-in Tools Implementation Plan

## Overview
The Consensus Agent currently only implements Google Drive custom tools. This plan outlines implementing all OpenAI built-in tools available in the Responses API to provide a comprehensive agent experience.

## Current State
- ✅ Google Drive custom tools (18 functions)
- ✅ Responses API implementation for custom tools
- ❌ No built-in tools implemented

## OpenAI Built-in Tools to Implement

### 1. Web Search Tool
**Type**: `web_search`
**Description**: Real-time web search for up-to-date information
**Usage**: Automatically triggered when current information is needed

### 2. Code Interpreter Tool  
**Type**: `code_interpreter`
**Description**: Execute Python code for calculations, data analysis, charts
**Usage**: Math, data analysis, visualization tasks

### 3. File Search Tool
**Type**: `file_search`
**Description**: Search within uploaded documents and vector stores
**Usage**: Knowledge base queries, document retrieval

### 4. Image Generation Tool
**Type**: `image_generation`
**Description**: Generate images using GPT-Image-1 model
**Usage**: Visual content creation, illustrations

### 5. Computer Use Tool
**Type**: `computer_use`
**Description**: Interact with operating system environments
**Usage**: Advanced automation tasks

### 6. Remote MCP Server Tool
**Type**: `mcp`
**Description**: Connect to Model Context Protocol servers
**Usage**: External system integrations (Shopify, Stripe, etc.)

## Implementation Strategy

### Phase 1: Core Built-in Tools (High Priority)
1. **Web Search** - Essential for current information
2. **Code Interpreter** - Math, analysis, visualization
3. **File Search** - Enhance existing knowledge base

### Phase 2: Visual & Advanced Tools (Medium Priority)
4. **Image Generation** - Visual content creation
5. **Computer Use** - Advanced automation

### Phase 3: Integration Tools (Future)
6. **MCP Server Support** - External integrations

## Technical Implementation

### 1. Update Orchestrator
- Add built-in tools configuration to `get_openai_response_with_tools()`
- Implement tool selection logic for built-in vs custom tools
- Handle mixed tool usage (built-in + custom)

### 2. Built-in Tools Configuration
```python
def _get_builtin_tools(self, enable_web_search=True, enable_code_interpreter=True, enable_file_search=True):
    """Configure OpenAI built-in tools"""
    tools = []
    
    if enable_web_search:
        tools.append({"type": "web_search"})
    
    if enable_code_interpreter:
        tools.append({
            "type": "code_interpreter",
            "container": {"type": "auto"}
        })
    
    if enable_file_search:
        tools.append({"type": "file_search"})
    
    return tools
```

### 3. Enhanced Tool Management
- Combine built-in tools with Google Drive custom tools
- Smart tool selection based on user query context
- Proper error handling for tool availability

## Integration Points

### Frontend Updates
- Add tool configuration options in admin panel
- Display tool usage indicators in chat
- Handle tool-specific responses (images, code results)

### Backend Updates  
- Update `LLMOrchestrator` for built-in tools
- Add tool configuration endpoints
- Enhance response processing for different tool types

### Configuration
- Environment variables for tool enablement
- User-level tool preferences
- Cost management for expensive tools

## Benefits

1. **Enhanced Capabilities**: Web search, code execution, image generation
2. **Better User Experience**: Comprehensive agent functionality
3. **Cost Efficiency**: Use built-in tools instead of custom implementations
4. **Future-Proof**: Leverage OpenAI's latest features
5. **Competitive Advantage**: Full-featured AI agent platform

## Pricing Considerations

- **Web Search**: Included in model usage
- **Code Interpreter**: $0.03 per container
- **File Search**: $0.10/GB storage + $2.50/1k tool calls
- **Image Generation**: $5/1M text tokens, $40/1M image tokens
- **Computer Use**: Model usage only

## Implementation Priority

1. **Immediate**: Web Search (free, high value)
2. **Short-term**: Code Interpreter (low cost, high utility)
3. **Medium-term**: File Search (enhance knowledge base)
4. **Future**: Image Generation & Computer Use

This implementation will transform the Consensus Agent from a Google Drive-focused tool into a comprehensive AI agent platform with full OpenAI capabilities.
