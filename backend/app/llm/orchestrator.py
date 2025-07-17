import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from app.config import settings
from openai import AsyncOpenAI
from pydantic import BaseModel

# Add Anthropic import for Claude models
ANTHROPIC_AVAILABLE = False
try:
    import anthropic  # type: ignore
    ANTHROPIC_AVAILABLE = True
except ImportError:
    pass

logger = logging.getLogger(__name__)

# Structured response schemas for consensus
class ModelResponse(BaseModel):
    content: str
    model: str
    confidence: float
    reasoning: str

class ConsensusResult(BaseModel):
    openai_response: ModelResponse
    grok_response: ModelResponse
    final_consensus: str
    confidence_score: float
    reasoning: str
    debate_points: List[str]

class LLMOrchestrator:
    """Orchestrates communication with multiple LLM providers"""
    
    def __init__(self):
        # Initialize OpenAI client
        self.openai_client = AsyncOpenAI(
            api_key=settings.openai_api_key
            # Remove org_id temporarily to avoid mismatch errors
            # organization=settings.openai_org_id if settings.openai_org_id else None
        )
        
        # Initialize Grok client (using httpx for HTTP requests)
        self.grok_base_url = "https://api.x.ai/v1"
        self.grok_headers = {
            "Authorization": f"Bearer {settings.grok_api_key}",
            "Content-Type": "application/json"
        }
        
        # Initialize Anthropic client for Claude models (if available)
        self.anthropic_client = None
        # Note: Anthropic SDK will be initialized when needed
        
        # Initialize DeepSeek client (uses OpenAI-compatible API)
        self.deepseek_client = None
        if settings.deepseek_api_key:
            try:
                self.deepseek_client = AsyncOpenAI(
                    api_key=settings.deepseek_api_key,
                    base_url="https://api.deepseek.com/v1"
                )
            except Exception as e:
                logger.warning(f"Failed to initialize DeepSeek client: {e}")
        
        # Initialize Google Drive tools - will be set later
        self.google_drive_tools = None
    
    def set_google_drive_tools(self, google_drive_tools):
        """Set Google Drive tools for function calling"""
        self.google_drive_tools = google_drive_tools
    
    def _supports_responses_api(self, model: str) -> bool:
        """Check if a model supports the Responses API with structured outputs"""
        # Models that support Responses API based on OpenAI documentation
        responses_api_models = [
            "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano",
            "o3", "o3-mini", "o4-mini", "o1",
            "gpt-4.1", "gpt-4.1-mini"  # These also support Responses API
        ]
        return model in responses_api_models
    
    def _get_google_drive_tools_for_openai(self) -> List[Dict[str, Any]]:
        """Get Google Drive function definitions formatted for OpenAI Chat Completions API"""
        if not self.google_drive_tools:
            return []
        
        functions = self.google_drive_tools.get_available_functions()
        openai_tools = []
        
        for func in functions:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": func.name,
                    "description": func.description,
                    "parameters": func.parameters
                }
            })
        
        return openai_tools
    
    def _get_google_drive_tools_for_responses_api(self) -> List[Dict[str, Any]]:
        """Get Google Drive function definitions formatted for OpenAI Responses API"""
        if not self.google_drive_tools:
            return []
        
        functions = self.google_drive_tools.get_available_functions()
        responses_tools = []
        
        for func in functions:
            # Ensure parameters have additionalProperties: false for strict mode
            parameters = func.parameters.copy() if func.parameters else {}
            if isinstance(parameters, dict) and parameters.get("type") == "object":
                parameters["additionalProperties"] = False
                
                # Also ensure nested objects have additionalProperties: false
                if "properties" in parameters:
                    for prop_name, prop_def in parameters["properties"].items():
                        if isinstance(prop_def, dict) and prop_def.get("type") == "object":
                            prop_def["additionalProperties"] = False
            
            responses_tools.append({
                "type": "function",
                "name": func.name,
                "description": func.description,
                "parameters": parameters,
                "strict": True  # Enable strict mode for better function calling
            })
        
        return responses_tools

    async def get_openai_response_with_builtin_tools(
        self, 
        prompt: str,
        model: str = "gpt-4.1",
        context: Optional[str] = None
    ) -> ModelResponse:
        """Get response from OpenAI using the Responses API with all built-in tools enabled"""
        
        try:
            logger.info(f"Using OpenAI Responses API with built-in tools for model: {model}")
            
            # Get current date
            current_date = datetime.now().strftime("%B %d, %Y")
            
            # Build comprehensive instructions that include tool awareness and current date
            instructions = f"""You are an advanced AI assistant with access to powerful built-in tools that enhance your capabilities.

📅 **Current Date**: Today is {current_date}

🔍 **Web Search**: You can search the internet for real-time information, current events, news, and up-to-date data. Use this when users ask for current information, recent news, or anything that requires live web data.

�️ **Image Generation**: You can create and generate images based on text descriptions. Use this when users ask for visual content, artwork, diagrams, or any image creation tasks.

🧮 **Code Interpreter**: You can run Python code, perform calculations, create visualizations, analyze data, and execute programming tasks in real-time. Use this for mathematical problems, data analysis, or computational tasks.

Important guidelines:
- Always use these tools when they would be helpful for answering the user's question
- For current events, news, or real-time information, use web search
- For visual requests or image creation, use image generation
- For calculations, data analysis, or programming tasks, use code interpreter
- Be proactive in using tools - don't just say you can't do something when you have the tools to do it
- When users ask about current information (like "latest news" or "recent events"), always use web search
- If asked about your capabilities, mention these specific tools you have access to"""

            # Prepare the full input with context if provided
            full_input = prompt
            if context:
                full_input = f"Context: {context}\n\nUser Query: {prompt}"

            # Use the Responses API with explicit tools configuration using official OpenAI syntax
            response = await self.openai_client.responses.create(
                model=model,
                instructions=instructions,
                input=full_input,
                tools=[
                    {"type": "web_search_preview"},
                    {
                        "type": "code_interpreter",
                        "container": {"type": "auto"}
                    }
                ]
            )
            
            # Extract content from response
            content = ""
            if hasattr(response, 'output_text'):
                content = response.output_text
            elif hasattr(response, 'output'):
                content = str(response.output)
            else:
                content = str(response)
            
            return ModelResponse(
                content=content,
                model=model,
                confidence=0.9,
                reasoning="OpenAI Responses API with built-in tools (web search, file search, code interpreter)"
            )
            
        except Exception as e:
            logger.error(f"OpenAI Responses API error: {e}")
            logger.info("Falling back to Responses API without explicit tools")
            
            # Fallback to Responses API without explicit tools but with instructions
            try:
                instructions = """You are an AI assistant. If you have access to tools like web search, file search, or code interpreter, use them when appropriate to provide the most helpful and current responses possible."""
                
                fallback_prompt = prompt
                if context:
                    fallback_prompt = f"{context}\n\n{prompt}"
                
                response = await self.openai_client.responses.create(
                    model=model,
                    instructions=instructions,
                    input=fallback_prompt
                )
                
                content = response.output_text if hasattr(response, 'output_text') else str(response)
                
                return ModelResponse(
                    content=content,
                    model=model,
                    confidence=0.8,
                    reasoning="OpenAI Responses API fallback"
                )
            except Exception as fallback_error:
                logger.error(f"OpenAI Responses API fallback failed: {fallback_error}")
                return ModelResponse(
                    content="I apologize, but I'm unable to process your request at the moment due to technical difficulties.",
                    model=model,
                    confidence=0.1,
                    reasoning="OpenAI API error"
                )

    async def get_openai_response(
        self, 
        prompt: str,
        model: str = "gpt-4.1",  # Use working model
        context: Optional[str] = None
    ) -> ModelResponse:
        """Get response from OpenAI using best available API for the model"""
        
        # Prepare the structured prompt for extracting confidence and reasoning
        structured_prompt = f"""
        {prompt}
        
        Please provide a clear, helpful response. Use markdown formatting naturally where it enhances readability:
        - Use headers only if you're organizing complex information into sections
        - Use lists only when presenting multiple related items or steps
        - Use code blocks only when showing actual code, commands, or structured data
        - Use emphasis (bold/italic) only for genuinely important points
        - Use blockquotes only when quoting sources or highlighting key information
        
        Focus on being natural and conversational while remaining informative and accurate.
        """
        
        try:
            # Try Responses API first for supported models
            if self._supports_responses_api(model):
                input_messages = []
                if context:
                    input_messages.append({
                        "role": "system",
                        "content": f"Context: {context}\n\nYou are a helpful AI assistant. Provide thoughtful, accurate responses."
                    })
                input_messages.append({
                    "role": "user", 
                    "content": structured_prompt
                })
                
                response = await self.openai_client.responses.create(
                    model=model,
                    input=input_messages,
                    text={
                        "format": {
                            "type": "json_schema",
                            "name": "model_response", 
                            "description": "Structured response from the model",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "content": {
                                        "type": "string",
                                        "description": "The main response content"
                                    },
                                    "confidence": {
                                        "type": "number",
                                        "minimum": 0,
                                        "maximum": 1,
                                        "description": "Confidence score for the response (0-1)"
                                    },
                                    "reasoning": {
                                        "type": "string", 
                                        "description": "Explanation of the reasoning behind the response"
                                    }
                                },
                                "required": ["content", "confidence", "reasoning"],
                                "additionalProperties": False
                            },
                            "strict": True
                        }
                    }
                )
                
                # Extract the structured response from the output
                import json
                try:
                    # Handle the response structure safely
                    response_text = str(response.output[0])  # type: ignore
                    # Try to extract text content if it's a more complex object
                    if hasattr(response.output[0], 'content'):  # type: ignore
                        if response.output[0].content and len(response.output[0].content) > 0:  # type: ignore
                            response_text = getattr(response.output[0].content[0], 'text', str(response.output[0].content[0]))  # type: ignore
                    elif hasattr(response.output[0], 'text'):  # type: ignore
                        response_text = response.output[0].text  # type: ignore
                    
                    response_data = json.loads(response_text)
                except (json.JSONDecodeError, AttributeError, IndexError) as parse_error:
                    logger.error(f"Failed to parse Responses API output: {parse_error}")
                    raise Exception(f"Invalid response format from Responses API: {parse_error}")
                
                return ModelResponse(
                    content=response_data["content"],
                    model=model,
                    confidence=response_data["confidence"],
                    reasoning=response_data["reasoning"]
                )
            
        except Exception as e:
            logger.error(f"OpenAI Responses API error: {e}")
        
        # Fallback to Chat Completions API (for all models or when Responses API fails)
        try:
            messages = []
            if context:
                messages.append({
                    "role": "system",
                    "content": f"Context: {context}\n\nYou are a helpful AI assistant. Provide thoughtful, accurate responses."
                })
            
            # Use JSON mode for structured output if available
            if model in ["gpt-4.1", "gpt-4.1-mini", "gpt-4-turbo", "gpt-3.5-turbo"]:
                messages.append({
                    "role": "user", 
                    "content": f"""{structured_prompt}

Please respond in JSON format:
{{
  "content": "your main response here in well-formatted Markdown",
  "confidence": 0.85,
  "reasoning": "brief explanation of your reasoning"
}}"""
                })
                
                fallback_response = await self.openai_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=64000,  # Increased for better responses
                    response_format={"type": "json_object"}
                )
                
                import json
                content_raw = fallback_response.choices[0].message.content
                if content_raw:
                    try:
                        response_data = json.loads(content_raw)
                        return ModelResponse(
                            content=response_data.get("content", content_raw),
                            model=model,
                            confidence=response_data.get("confidence", 0.8),
                            reasoning=response_data.get("reasoning", "Chat Completions API with JSON mode")
                        )
                    except json.JSONDecodeError:
                        # Fall through to plain text handling
                        pass
            
            # Plain text fallback
            messages.append({
                "role": "user", 
                "content": f"""
                {prompt}
                
                Please format your response in clear, well-structured Markdown for easy reading.
                Use appropriate headers, lists, code blocks, and emphasis where helpful.
                """
            })
            
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=64000  # Increased for better responses
            )
            
            content = response.choices[0].message.content or "No response content"
            
            return ModelResponse(
                content=content,
                model=model,
                confidence=0.8,
                reasoning="Responses API fallback"
            )
            
        except Exception as fallback_error:
            logger.error(f"Fallback OpenAI API error: {fallback_error}")
            return ModelResponse(
                content=f"Error getting OpenAI response: {str(fallback_error)}",
                model=model,
                confidence=0.0,
                reasoning="API error occurred"
            )
    
    async def get_grok_response(
        self, 
        prompt: str,
        model: str = "grok-3-latest",  # Use working model
        context: Optional[str] = None
    ) -> ModelResponse:
        """Get response from Grok using xAI API"""
        try:
            # Prepare messages with context if provided
            messages = []
            if context:
                messages.append({"role": "system", "content": f"Context: {context}"})
            
            formatted_prompt = f"""
            {prompt}
            
            Please provide a helpful, natural response. Use markdown formatting only when it genuinely improves clarity:
            - Headers for organizing complex topics into clear sections
            - Lists when presenting multiple related items or sequential steps  
            - Code blocks when showing actual code, commands, or technical examples
            - Tables when comparing data or presenting structured information
            - Emphasis when highlighting truly important points
            
            Be conversational and focus on directly answering the question rather than forcing formatting.
            """
            
            messages.append({"role": "user", "content": formatted_prompt})
            
            # Make request to Grok API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.grok_base_url}/chat/completions",
                    headers=self.grok_headers,
                    json={
                        "model": model,
                        "messages": messages,
                        "stream": False,
                        "temperature": 0.7,
                        "max_tokens": 64000  # Increased for better responses
                    },
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    raise Exception(f"Grok API error: {response.status_code} - {response.text}")
                
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                return ModelResponse(
                    content=content,
                    model=model,
                    confidence=0.8,  # Default confidence for Grok
                    reasoning="Grok response"
                )
                
        except Exception as e:
            logger.error(f"Grok API error: {e}")
            return ModelResponse(
                content=f"Error getting Grok response: {str(e)}",
                model=model,
                confidence=0.0,
                reasoning="API error occurred"
            )
    
    async def get_grok_response_with_tools(
        self, 
        prompt: str,
        model: str = "grok-2-1212",  # Use latest Grok model with tool support
        context: Optional[str] = None
    ) -> ModelResponse:
        """Get response from Grok using xAI API with built-in tools and function calling"""
        try:
            # Prepare messages with context if provided
            messages = []
            if context:
                messages.append({"role": "system", "content": f"Context: {context}"})
            
            # Enable Grok's built-in capabilities through enhanced prompt
            current_date = datetime.now().strftime("%B %d, %Y")
            enhanced_prompt = f"""You are Grok, an AI assistant with access to powerful built-in capabilities:

📅 **Current Date**: Today is {current_date}

🌐 **Real-time Web Search**: You can search the internet for current information, breaking news, and recent events. Always use this for questions about current events, recent news, or anything requiring up-to-date information.

🖼️ **Image Generation**: You can create and generate images based on text descriptions. Offer to create visualizations when appropriate.

📱 **X/Twitter Integration**: You have access to real-time posts and trending topics from X (Twitter) for the most current social media insights.

User's request: {prompt}

Guidelines:
- Proactively use these tools when they would be helpful
- For any question about current events, news, or recent information, always use web search
- Be direct about your capabilities - don't say you can't access current information when you can
- Provide comprehensive, up-to-date responses using your tools
- Format responses clearly with markdown when it improves readability

Remember: You have access to real-time information and can search the web, so use these capabilities to provide the most current and helpful responses possible."""
            
            messages.append({"role": "user", "content": enhanced_prompt})
            
            # Add Google Drive tools if available for function calling
            tools = []
            if self.google_drive_tools:
                # Check if it's a list or a single object with methods
                if isinstance(self.google_drive_tools, list):
                    tools.extend(self.google_drive_tools)
                elif hasattr(self.google_drive_tools, 'get_tool_definitions'):
                    # If it's a GoogleDriveTools object, get its tool definitions
                    try:
                        drive_tools = self.google_drive_tools.get_tool_definitions()
                        if isinstance(drive_tools, list):
                            tools.extend(drive_tools)
                    except (AttributeError, TypeError) as e:
                        logger.warning(f"Could not get GoogleDriveTools definitions: {e}")
                else:
                    logger.warning(f"GoogleDriveTools is not iterable or callable: {type(self.google_drive_tools)}")
            
            # Note: Grok has built-in web search, so we primarily rely on that
            # Custom tools are for specific functions like Google Drive integration
            
            # Prepare request payload with Live Search enabled
            request_data = {
                "model": model,
                "messages": messages,
                "stream": False,
                "temperature": 0.7,
                "max_tokens": 64000,
                # Enable Grok's Live Search for real-time web search
                "search_parameters": {
                    "mode": "auto",  # Let Grok decide when to search
                    "return_citations": True,
                    "max_search_results": 10,
                    "sources": [
                        {"type": "web"},
                        {"type": "x"}  # Include X/Twitter search
                    ]
                }
            }
            
            # Add tools if available (Grok supports function calling)
            if tools:
                request_data["tools"] = tools
                request_data["tool_choice"] = "auto"
            
            # Make request to Grok API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.grok_base_url}/chat/completions",
                    headers=self.grok_headers,
                    json=request_data,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    raise Exception(f"Grok API error: {response.status_code} - {response.text}")
                
                data = response.json()
                choice = data["choices"][0]
                
                # Handle function calls if present
                if choice["message"].get("tool_calls"):
                    # Function calling logic would go here
                    content = choice["message"]["content"] or "Function calling response processed"
                else:
                    content = choice["message"]["content"]
                
                return ModelResponse(
                    content=content,
                    model=model,
                    confidence=0.9,  # Higher confidence with tools
                    reasoning="Grok response with built-in tools (web search, real-time data, image generation)"
                )
                
        except Exception as e:
            logger.error(f"Grok API with tools error: {e}")
            # Fallback to basic Grok response
            return await self.get_grok_response(prompt, model, context)

    async def get_claude_response_with_tools(
        self, 
        prompt: str,
        model: str = "claude-3-5-sonnet-20241022",
        context: Optional[str] = None
    ) -> ModelResponse:
        """Get response from Claude using Anthropic API with built-in tools"""
        try:
            # Fallback to basic implementation using httpx
            headers = {
                "Authorization": f"Bearer {settings.anthropic_api_key}",
                "Content-Type": "application/json",
                "x-api-key": settings.anthropic_api_key,
                "anthropic-version": "2023-06-01",
                "anthropic-beta": "web-search-20250305"
            }

            # Create enhanced prompt that informs Claude about its tool capabilities
            current_date = datetime.now().strftime("%B %d, %Y")
            system_message = f"""You are Claude, an AI assistant with access to advanced built-in tools:

📅 **Current Date**: Today is {current_date}

🖥️ **Computer Use**: You can take screenshots, click buttons, type text, and interact with computer interfaces directly.

🔍 **Web Search**: You can search the internet for current information, recent news, and real-time data.

📝 **Text Editor**: You can create, edit, and manipulate text files and documents.

⚡ **Bash Terminal**: You can execute command-line operations and scripts.

Guidelines:
- Use these tools proactively when they would help answer the user's question
- For current events or recent information, use web search
- For computational tasks, use the appropriate tools
- Be direct about your capabilities - you have access to real-time tools

Remember: You are not limited to your training data - you can access current information and interact with systems in real-time."""

            messages = []
            if context:
                enhanced_prompt = f"Context: {context}\n\nUser Request: {prompt}"
            else:
                enhanced_prompt = prompt
                
            messages.append({"role": "user", "content": enhanced_prompt})
            
            # Add web search and other built-in tools
            tools = [
                {
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": 5
                },
                {
                    "type": "computer_20241022",
                    "name": "computer",
                    "display_width_px": 1024,
                    "display_height_px": 768,
                    "display_number": 1
                },
                {
                    "type": "text_editor_20241022", 
                    "name": "str_replace_editor"
                },
                {
                    "type": "bash_20241022",
                    "name": "bash"
                }
            ]
            
            request_data = {
                "model": model,
                "max_tokens": 2000,
                "messages": messages,
                "system": system_message,
                "tools": tools
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=request_data,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    raise Exception(f"Claude API error: {response.status_code} - {response.text}")
                
                data = response.json()
                content = ""
                
                # Extract content from response
                for block in data.get("content", []):
                    if block.get("type") == "text":
                        content += block.get("text", "")
                
                return ModelResponse(
                    content=content,
                    model=model,
                    confidence=0.9,
                    reasoning="Claude response with built-in capabilities"
                )
            
        except Exception as e:
            logger.error(f"Claude API with tools error: {e}")
            return ModelResponse(
                content=f"Error getting Claude response: {str(e)}",
                model=model,
                confidence=0.0,
                reasoning="API error occurred"
            )

    async def get_deepseek_response_with_tools(
        self, 
        prompt: str,
        model: str = "deepseek-chat",
        context: Optional[str] = None
    ) -> ModelResponse:
        """Get response from DeepSeek using their API with function calling support"""
        try:
            # Check if DeepSeek client is available
            if not self.deepseek_client:
                logger.warning("DeepSeek client not initialized. Check API key configuration.")
                return ModelResponse(
                    content="DeepSeek API not configured. Please set API key.",
                    model=model,
                    confidence=0.0,
                    reasoning="DeepSeek API not configured"
                )
            
            # Prepare messages
            messages = []
            if context:
                messages.append({"role": "system", "content": f"Context: {context}"})
            
            # Enhanced prompt for DeepSeek reasoning and function calling capabilities
            current_date = datetime.now().strftime("%B %d, %Y")
            enhanced_prompt = f"""You are DeepSeek, an advanced AI assistant with sophisticated reasoning and function calling capabilities:

📅 **Current Date**: Today is {current_date}

🔧 **Function Calling**: You can call external functions and APIs to access real-time data, perform actions, and integrate with various services.

🧠 **Deep Reasoning**: You excel at complex reasoning, mathematical problem-solving, and analytical thinking.

📊 **Data Analysis**: You can process and analyze data through function calls when appropriate tools are available.

User's request: {prompt}

Guidelines:
- Use function calling when available tools can help answer the question
- Apply deep reasoning to complex problems
- Be methodical and thorough in your analysis
- If you have access to external functions or APIs, use them proactively to provide more comprehensive and current responses
- Explain your reasoning process when solving complex problems

Remember: You have function calling capabilities - use them when they would enhance your response with real-time data or external services."""
            
            messages.append({"role": "user", "content": enhanced_prompt})
            
            # Add Google Drive tools if available (DeepSeek supports function calling)
            tools = []
            if self.google_drive_tools:
                tools.extend(self.google_drive_tools)
            
            # Prepare request
            request_kwargs = {
                "model": model,
                "messages": messages,  # type: ignore
                "temperature": 0.7,
                "max_tokens": 4000
            }
            
            # Add tools if available
            if tools:
                request_kwargs["tools"] = tools  # type: ignore
                request_kwargs["tool_choice"] = "auto"  # type: ignore
            
            # Make request to DeepSeek API
            response = await self.deepseek_client.chat.completions.create(**request_kwargs)
            
            # Handle function calls if present
            choice = response.choices[0]
            if choice.message.tool_calls:
                # Function calling logic would go here
                content = choice.message.content or "Function calling response processed"
            else:
                content = choice.message.content or ""
            
            return ModelResponse(
                content=content,
                model=model,
                confidence=0.85,  # Good confidence with reasoning model
                reasoning="DeepSeek response with reasoning capabilities and function calling"
            )
            
        except Exception as e:
            logger.error(f"DeepSeek API with tools error: {e}")
            return ModelResponse(
                content=f"Error getting DeepSeek response: {str(e)}",
                model=model,
                confidence=0.0,
                reasoning="API error occurred"
            )
    
    async def generate_consensus_dynamic(
        self, 
        prompt: str,
        selected_models: List[str],
        context: Optional[str] = None
    ) -> ConsensusResult:
        """Generate consensus response from dynamically selected models with their tool capabilities"""
        
        logger.info(f"Starting dynamic consensus generation for prompt: {prompt[:100]}...")
        logger.info(f"Selected models: {selected_models}")
        
        if len(selected_models) < 2:
            raise ValueError("Consensus requires at least 2 models")
        
        # Get responses from all selected models in parallel with their tool capabilities
        tasks = []
        model_types = []
        
        for model in selected_models:
            if model.startswith("gpt") or model.startswith("o1") or model.startswith("o3"):
                tasks.append(self.get_openai_response_with_builtin_tools(prompt, model, context))
                model_types.append("openai")
            elif model.startswith("grok"):
                tasks.append(self.get_grok_response_with_tools(prompt, model, context))
                model_types.append("grok")
            elif model.startswith("claude"):
                tasks.append(self.get_claude_response_with_tools(prompt, model, context))
                model_types.append("claude")
            elif model.startswith("deepseek"):
                tasks.append(self.get_deepseek_response_with_tools(prompt, model, context))
                model_types.append("deepseek")
            else:
                # Fallback to OpenAI for unknown models
                tasks.append(self.get_openai_response_with_builtin_tools(prompt, model, context))
                model_types.append("openai")
        
        logger.info(f"Fetching responses from {len(tasks)} models with their respective tool capabilities...")
        responses = await asyncio.gather(*tasks)
        
        # Log confidence scores
        for i, response in enumerate(responses):
            logger.info(f"{selected_models[i]} response confidence: {response.confidence}")
        
        # Check how many responses are valid
        valid_responses = [r for r in responses if r.confidence > 0]
        
        # Enhanced consensus generation with debate simulation
        current_date = datetime.now().strftime("%B %d, %Y")
        
        if len(valid_responses) >= 2:
            # Build consensus prompt with all model responses
            model_responses_text = ""
            for i, response in enumerate(responses):
                if response.confidence > 0:
                    model_responses_text += f"""
{selected_models[i]} Response (Confidence: {response.confidence}):
{response.content}
Reasoning: {response.reasoning}
Tool Capabilities: {model_types[i]} - {'✅ Real-time tools' if model_types[i] in ['openai', 'grok', 'claude'] else '❌ No real-time tools'}

"""
            
            consensus_prompt = f"""
            You are an expert analyst creating consensus from multiple AI responses. Today is {current_date}.
            
            Analyze these responses and create a comprehensive consensus that leverages the tool capabilities of each model.
            
            User Question: {prompt}
            
            {model_responses_text}
            
            Please perform the following analysis:
            1. Identify key agreements between the responses
            2. Identify any contradictions or disagreements  
            3. Evaluate the strengths of each response and their tool usage
            4. Note which models had access to real-time information vs training data only
            5. Create a synthesized consensus that combines the best insights from all models
            6. Assign a confidence score based on agreement and quality
            7. List specific debate points if disagreements exist
            
            Provide your response in the following JSON format:
            {{
                "final_consensus": "your comprehensive consensus response here",
                "confidence_score": 0.85,
                "reasoning": "detailed explanation of your analysis and synthesis process",
                "debate_points": ["specific point of disagreement 1", "specific point of disagreement 2"]
            }}
            """
        else:
            # Fallback when most models failed
            working_responses = [r for r in responses if r.confidence > 0]
            if working_responses:
                working_response = working_responses[0]
                working_model_idx = responses.index(working_response)
                working_model = selected_models[working_model_idx]
                
                consensus_prompt = f"""
                You are an expert analyst. Today is {current_date}. Limited AI responses available for the user's question.
                
                User Question: {prompt}
                
                Available Response from {working_model}:
                {working_response.content}
                Confidence: {working_response.confidence}
                Reasoning: {working_response.reasoning}
                Tool Capabilities: {model_types[working_model_idx]} - {'✅ Real-time tools' if model_types[working_model_idx] in ['openai', 'grok', 'claude'] else '❌ No real-time tools'}
                
                Please enhance and validate this response:
                1. Review the response for accuracy and completeness
                2. Note the tool capabilities that were available to this model
                3. Add any missing important information
                4. Provide a confidence assessment
                5. Note limitations due to limited model availability
                
                Provide your response in the following JSON format:
                {{
                    "final_consensus": "your enhanced and validated response here",
                    "confidence_score": 0.70,
                    "reasoning": "explanation of validation and any enhancements made",
                    "debate_points": ["limitation: few working models", "note: consensus limited by model failures"]
                }}
                """
            else:
                # All models failed
                consensus_prompt = f"""
                All selected models failed to respond. Please provide a helpful message to the user.
                
                User Question: {prompt}
                Selected Models: {', '.join(selected_models)}
                
                Provide your response in the following JSON format:
                {{
                    "final_consensus": "I apologize, but all selected AI models are currently unavailable. Please try again later or select different models.",
                    "confidence_score": 0.0,
                    "reasoning": "All models failed to respond",
                    "debate_points": ["All models unavailable", "System error - no responses received"]
                }}
                """
        
        try:
            # Use grok-3-latest as judge model for consensus analysis
            logger.info("Generating consensus using Grok 3 judge model...")
            
            # Prepare Grok request for consensus analysis
            grok_headers = {
                "Authorization": f"Bearer {settings.grok_api_key}",
                "Content-Type": "application/json"
            }
            
            grok_request = {
                "model": "grok-3-latest",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert analyst that creates consensus from multiple AI responses with different tool capabilities. Always respond with valid JSON in the requested format. Be thorough in your analysis and synthesis, paying special attention to which models had access to real-time tools vs training data only."
                    },
                    {
                        "role": "user", 
                        "content": consensus_prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 2000,
                "response_format": {"type": "json_object"}
            }
            
            async with httpx.AsyncClient() as client:
                consensus_response = await client.post(
                    f"{self.grok_base_url}/chat/completions",
                    headers=grok_headers,
                    json=grok_request,
                    timeout=30.0
                )
                
                if consensus_response.status_code != 200:
                    raise Exception(f"Grok consensus API error: {consensus_response.status_code} - {consensus_response.text}")
                
                grok_data = consensus_response.json()
                consensus_content = grok_data["choices"][0]["message"]["content"]
                
                import json
            if not consensus_content:
                raise Exception("Empty consensus response")
            
            # Enhanced JSON parsing with error handling
            try:
                consensus_data = json.loads(consensus_content)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {e}")
                logger.error(f"Raw consensus content: {consensus_content}")
                # If JSON parsing fails, create a structured fallback
                consensus_data = {
                    "final_consensus": consensus_content,  # Use raw content as fallback
                    "confidence_score": 0.6,
                    "reasoning": "JSON parsing failed, using raw model response",
                    "debate_points": ["Unable to parse structured consensus response"]
                }
            
            # Validate that consensus_data is a dictionary
            if not isinstance(consensus_data, dict):
                logger.error(f"Consensus data is not a dictionary: {type(consensus_data)}")
                consensus_data = {
                    "final_consensus": str(consensus_data),
                    "confidence_score": 0.5,
                    "reasoning": "Invalid response format, converted to string",
                    "debate_points": ["Response format validation failed"]
                }
            
            # Ensure final_consensus is a string (handle cases where judge returns complex structure)
            final_consensus = consensus_data.get("final_consensus", "")
            if isinstance(final_consensus, dict):
                # Convert dict response to formatted string
                if "pros" in final_consensus and "cons" in final_consensus:
                    pros = "\n".join([f"• {item}" for item in final_consensus.get("pros", [])])
                    cons = "\n".join([f"• {item}" for item in final_consensus.get("cons", [])])
                    final_consensus = f"**Pros:**\n{pros}\n\n**Cons:**\n{cons}"
                else:
                    final_consensus = str(final_consensus)
            
            # Additional safety: ensure we never return raw JSON
            if not final_consensus or final_consensus.strip().startswith('{'):
                logger.warning("Final consensus appears to be JSON or empty, creating fallback response")
                # Create a fallback response that summarizes the consensus data
                final_consensus = f"""Based on analysis from {len(selected_models)} AI models:

**Summary:** {consensus_data.get('reasoning', 'AI consensus analysis completed')}

**Confidence Level:** {consensus_data.get('confidence_score', 0.5) * 100:.0f}%

This response represents a synthesis of insights from multiple AI perspectives with their respective tool capabilities."""
            
            logger.info(f"Dynamic consensus generated with confidence: {consensus_data.get('confidence_score', 0.5)}")
            logger.info(f"Final consensus preview: {final_consensus[:100]}...")
            
            # Create response structure compatible with existing ConsensusResult
            # For backward compatibility, we'll use the first two responses as openai/grok responses
            openai_response = responses[0] if len(responses) > 0 else ModelResponse(
                content="Model unavailable", model=selected_models[0] if selected_models else "unknown", 
                confidence=0.0, reasoning="Model failed"
            )
            grok_response = responses[1] if len(responses) > 1 else ModelResponse(
                content="Model unavailable", model=selected_models[1] if len(selected_models) > 1 else "unknown",
                confidence=0.0, reasoning="Model failed"
            )
            
            return ConsensusResult(
                openai_response=openai_response,
                grok_response=grok_response,
                final_consensus=final_consensus,
                confidence_score=consensus_data.get("confidence_score", 0.5),
                reasoning=consensus_data.get("reasoning", "") + f" | Models: {', '.join(selected_models)}",
                debate_points=consensus_data.get("debate_points", [])
            )
            
        except Exception as e:
            logger.error(f"Grok consensus generation error: {e}")
            # Enhanced fallback: create a more intelligent combination
            
            valid_responses = [r for r in responses if r.confidence > 0]
            if len(valid_responses) >= 2:
                # Multiple responses are valid - create a simple synthesis
                consensus_text = f"""Based on {len(valid_responses)} AI model analysis:

**Key Insights:**
"""
                for i, response in enumerate(responses):
                    if response.confidence > 0:
                        model_name = selected_models[i]
                        tools_info = "🔍 Real-time tools" if model_types[i] in ['openai', 'grok', 'claude'] else "📚 Training data only"
                        consensus_text += f"\n**{model_name}** ({tools_info}):\n{response.content[:300]}...\n"
                
                consensus_text += f"\n**Summary:** This response combines insights from {len(valid_responses)} AI models with varying tool capabilities."
                confidence = sum(r.confidence for r in valid_responses) / len(valid_responses)
                reasoning = f"Fallback synthesis of {len(valid_responses)} models: {', '.join(selected_models)}"
                debate_points = ["Unable to perform detailed consensus analysis due to processing error"]
            elif len(valid_responses) == 1:
                # Only one response is valid
                working_response = valid_responses[0]
                working_model_idx = next(i for i, r in enumerate(responses) if r.confidence > 0)
                working_model = selected_models[working_model_idx]
                tools_info = "🔍 Real-time tools" if model_types[working_model_idx] in ['openai', 'grok', 'claude'] else "📚 Training data only"
                
                consensus_text = f"""Single model response ({tools_info}):

{working_response.content}

Note: This response is from {working_model} only due to other models being unavailable."""
                confidence = working_response.confidence * 0.8  # Reduce confidence for single model
                reasoning = f"Single model fallback using {working_model} due to other model failures"
                debate_points = ["Single model response due to consensus failure", "Reduced reliability without model comparison"]
            else:
                # All models failed
                consensus_text = f"""All selected models ({', '.join(selected_models)}) are currently unavailable. Please try again later or select different models."""
                confidence = 0.0
                reasoning = "All models failed to respond"
                debate_points = ["All models unavailable", "System error - no responses received"]
            
            # Create compatible response structure
            openai_response = responses[0] if len(responses) > 0 else ModelResponse(
                content="Model unavailable", model=selected_models[0] if selected_models else "unknown", 
                confidence=0.0, reasoning="Model failed"
            )
            grok_response = responses[1] if len(responses) > 1 else ModelResponse(
                content="Model unavailable", model=selected_models[1] if len(selected_models) > 1 else "unknown",
                confidence=0.0, reasoning="Model failed"
            )
            
            return ConsensusResult(
                openai_response=openai_response,
                grok_response=grok_response,
                final_consensus=consensus_text,
                confidence_score=confidence,
                reasoning=reasoning,
                debate_points=debate_points
            )

    async def generate_consensus(
        self, 
        prompt: str,
        context: Optional[str] = None,
        openai_model: str = "gpt-4.1",  # Use working model
        grok_model: str = "grok-3-latest"   # Use working model
    ) -> ConsensusResult:
        """Generate consensus response from multiple models with debate simulation"""
        
        logger.info(f"Starting consensus generation for prompt: {prompt[:100]}...")
        
        # Get responses from both models in parallel
        logger.info("Fetching responses from OpenAI and Grok with enhanced tools...")
        openai_task = self.get_openai_response_with_builtin_tools(prompt, openai_model, context)
        grok_task = self.get_grok_response_with_tools(prompt, grok_model, context)
        
        openai_response, grok_response = await asyncio.gather(openai_task, grok_task)
        
        logger.info(f"OpenAI response confidence: {openai_response.confidence}")
        logger.info(f"Grok response confidence: {grok_response.confidence}")
        
        # Check if both responses are valid
        both_valid = (openai_response.confidence > 0 and grok_response.confidence > 0)
        
        # Enhanced consensus generation with debate simulation
        current_date = datetime.now().strftime("%B %d, %Y")
        if both_valid:
            consensus_prompt = f"""
            You are an expert analyst creating consensus from multiple AI responses. Today is {current_date}.
            
            Analyze these responses and create a comprehensive consensus.
            
            User Question: {prompt}
            
            OpenAI Response (Confidence: {openai_response.confidence}):
            {openai_response.content}
            Reasoning: {openai_response.reasoning}
            
            Grok Response (Confidence: {grok_response.confidence}):
            {grok_response.content}
            Reasoning: {grok_response.reasoning}
            
            Please perform the following analysis:
            1. Identify key agreements between the responses
            2. Identify any contradictions or disagreements
            3. Evaluate the strengths of each response
            4. Create a synthesized consensus that combines the best insights
            5. Assign a confidence score based on agreement and quality
            6. List specific debate points if disagreements exist
            
            Provide your response in the following JSON format:
            {{
                "final_consensus": "your comprehensive consensus response here",
                "confidence_score": 0.85,
                "reasoning": "detailed explanation of your analysis and synthesis process",
                "debate_points": ["specific point of disagreement 1", "specific point of disagreement 2"]
            }}
            """
        else:
            # Fallback when one or both models failed
            working_response = openai_response if openai_response.confidence > 0 else grok_response
            consensus_prompt = f"""
            You are an expert analyst. Today is {current_date}. One AI response is available for the user's question.
            
            User Question: {prompt}
            
            Available Response:
            {working_response.content}
            Confidence: {working_response.confidence}
            Reasoning: {working_response.reasoning}
            
            Please enhance and validate this response:
            1. Review the response for accuracy and completeness
            2. Add any missing important information
            3. Provide a confidence assessment
            4. Note any limitations due to single-source analysis
            
            Provide your response in the following JSON format:
            {{
                "final_consensus": "your enhanced and validated response here",
                "confidence_score": 0.75,
                "reasoning": "explanation of validation and any enhancements made",
                "debate_points": ["limitation: single model response", "note: consensus limited by model failure"]
            }}
            """
        
        try:
            # Use o3 as judge model for superior reasoning and consensus analysis
            logger.info("Generating consensus using o3 judge model...")
            consensus_response = await self.openai_client.chat.completions.create(
                model="o3",  # Use o3 for best reasoning and synthesis capabilities
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert analyst that creates consensus from multiple AI responses. Always respond with valid JSON in the requested format. Be thorough in your analysis and synthesis."
                    },
                    {
                        "role": "user", 
                        "content": consensus_prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            import json
            consensus_content = consensus_response.choices[0].message.content
            if not consensus_content:
                raise Exception("Empty consensus response")
            
            # Enhanced JSON parsing with error handling
            try:
                consensus_data = json.loads(consensus_content)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {e}")
                logger.error(f"Raw consensus content: {consensus_content}")
                # If JSON parsing fails, create a structured fallback
                consensus_data = {
                    "final_consensus": consensus_content,  # Use raw content as fallback
                    "confidence_score": 0.6,
                    "reasoning": "JSON parsing failed, using raw model response",
                    "debate_points": ["Unable to parse structured consensus response"]
                }
            
            # Validate that consensus_data is a dictionary
            if not isinstance(consensus_data, dict):
                logger.error(f"Consensus data is not a dictionary: {type(consensus_data)}")
                consensus_data = {
                    "final_consensus": str(consensus_data),
                    "confidence_score": 0.5,
                    "reasoning": "Invalid response format, converted to string",
                    "debate_points": ["Response format validation failed"]
                }
            
            # Ensure final_consensus is a string (handle cases where judge returns complex structure)
            final_consensus = consensus_data.get("final_consensus", "")
            if isinstance(final_consensus, dict):
                # Convert dict response to formatted string
                if "pros" in final_consensus and "cons" in final_consensus:
                    pros = "\n".join([f"• {item}" for item in final_consensus.get("pros", [])])
                    cons = "\n".join([f"• {item}" for item in final_consensus.get("cons", [])])
                    final_consensus = f"**Pros:**\n{pros}\n\n**Cons:**\n{cons}"
                else:
                    final_consensus = str(final_consensus)
            
            # Additional safety: ensure we never return raw JSON
            if not final_consensus or final_consensus.strip().startswith('{'):
                logger.warning("Final consensus appears to be JSON or empty, creating fallback response")
                # Create a fallback response that summarizes the consensus data
                final_consensus = f"""Based on analysis from multiple AI models:

**Summary:** {consensus_data.get('reasoning', 'AI consensus analysis completed')}

**Confidence Level:** {consensus_data.get('confidence_score', 0.5) * 100:.0f}%

This response represents a synthesis of insights from multiple AI perspectives."""
            
            logger.info(f"Consensus generated with confidence: {consensus_data.get('confidence_score', 0.5)}")
            logger.info(f"Final consensus preview: {final_consensus[:100]}...")
            
            return ConsensusResult(
                openai_response=openai_response,
                grok_response=grok_response,
                final_consensus=final_consensus,
                confidence_score=consensus_data.get("confidence_score", 0.5),
                reasoning=consensus_data.get("reasoning", ""),
                debate_points=consensus_data.get("debate_points", [])
            )
            
        except Exception as e:
            logger.error(f"Consensus generation error: {e}")
            # Enhanced fallback: create a more intelligent combination
            
            if both_valid:
                # Both responses are valid - create a simple synthesis
                consensus_text = f"""Based on multiple AI analysis:

**Key Insights:**
{openai_response.content}

**Additional Perspective:**
{grok_response.content}

**Summary:** This response combines insights from multiple AI models to provide a comprehensive answer."""
                confidence = (openai_response.confidence + grok_response.confidence) / 2
                reasoning = f"Fallback synthesis of {openai_model} (confidence: {openai_response.confidence}) and {grok_model} (confidence: {grok_response.confidence})"
                debate_points = ["Unable to perform detailed consensus analysis due to processing error"]
            else:
                # Only one response is valid
                working_response = openai_response if openai_response.confidence > 0 else grok_response
                working_model = openai_model if openai_response.confidence > 0 else grok_model
                consensus_text = f"""Single model response (other model failed):

{working_response.content}

Note: This response is from {working_model} only due to the other model being unavailable."""
                confidence = working_response.confidence * 0.8  # Reduce confidence for single model
                reasoning = f"Single model fallback using {working_model} due to model failure"
                debate_points = ["Single model response due to consensus failure", "Reduced reliability without model comparison"]
            
            return ConsensusResult(
                openai_response=openai_response,
                grok_response=grok_response,
                final_consensus=consensus_text,
                confidence_score=confidence,
                reasoning=reasoning,
                debate_points=debate_points
            )
    
    async def get_openai_response_with_tools(
        self, 
        prompt: str,
        user,  # User object for Google Drive operations
        model: str = "gpt-4.1-mini",  # Use gpt-4.1-mini for better function calling performance
        context: Optional[str] = None,
        enable_google_drive: bool = True
    ) -> ModelResponse:
        """Get response from OpenAI with Google Drive function calling support using multi-step function calling loop"""
        
        # Build initial messages
        messages = []
        if context:
            messages.append({
                "role": "system",
                "content": f"Context: {context}\n\nYou are a helpful AI assistant with access to Google Drive. You can read, edit, create, copy, move, and manage Google Drive files when requested by the user.\n\nIMPORTANT: When the user asks you to perform multi-step file operations (like copying files, moving files, or complex searches), you should use multiple function calls as needed to complete the entire task. You can call functions in sequence or parallel to accomplish complex workflows.\n\nAvailable capabilities:\n- Search for files by name or content in all folders\n- Find folders by name\n- List folder contents\n- Copy files to different locations\n- Move files between folders\n- Read, edit, and create documents\n- Get file paths and organization\n\nUse the available functions to complete the user's requests fully. You can make multiple function calls to accomplish complex tasks."
            })
        else:
            messages.append({
                "role": "system", 
                "content": "You are a helpful AI assistant with access to Google Drive. You can read, edit, create, copy, move, and manage Google Drive files when requested by the user.\n\nIMPORTANT: When the user asks you to perform multi-step file operations (like copying files, moving files, or complex searches), you should use multiple function calls as needed to complete the entire task. You can call functions in sequence or parallel to accomplish complex workflows.\n\nAvailable capabilities:\n- Search for files by name or content in all folders\n- Find folders by name\n- List folder contents\n- Copy files to different locations\n- Move files between folders\n- Read, edit, and create documents\n- Get file paths and organization\n\nUse the available functions to complete the user's requests fully. You can make multiple function calls to accomplish complex tasks."
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Get Google Drive tools if enabled and available
        tools = []
        if enable_google_drive and self.google_drive_tools:
            tools = self._get_google_drive_tools_for_openai()
        
        try:
            # Use Chat Completions API with function calling loop
            logger.info(f"Using Chat Completions API for {model} with {len(tools)} tools")
            
            # Function calling loop - continue until no more function calls are needed
            max_iterations = 10  # Prevent infinite loops
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                logger.info(f"Function calling iteration {iteration}")
                
                # Prepare API call
                kwargs = {
                    "model": model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 4000
                }
                
                if tools:
                    kwargs["tools"] = tools
                    kwargs["tool_choice"] = "auto"  # Let model decide when to use tools
                    kwargs["parallel_tool_calls"] = True  # Enable parallel function calling
                
                # Make API call with timeout
                import asyncio
                response = await asyncio.wait_for(
                    self.openai_client.chat.completions.create(**kwargs),
                    timeout=30.0
                )
                
                # Check if the model wants to call functions
                if response.choices[0].message.tool_calls:
                    logger.info(f"Model requested {len(response.choices[0].message.tool_calls)} function calls")
                    
                    # Add assistant message with tool calls to conversation
                    messages.append(response.choices[0].message)
                    
                    # Execute all tool calls (can be parallel)
                    for tool_call in response.choices[0].message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        
                        logger.info(f"Executing function: {function_name} with args: {function_args}")
                        
                        # Execute Google Drive function
                        if self.google_drive_tools:
                            tool_result = await self.google_drive_tools.execute_function(
                                function_name, function_args, user
                            )
                            
                            # Add tool result to conversation
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps({
                                    "success": tool_result.success,
                                    "message": tool_result.message,
                                    "data": tool_result.data,
                                    "error": tool_result.error
                                })
                            })
                            
                            logger.info(f"Function {function_name} result: {tool_result.success}")
                        else:
                            # Add error message if tools not available
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps({
                                    "success": False,
                                    "message": "Google Drive tools not available",
                                    "error": "NO_TOOLS"
                                })
                            })
                    
                    # Continue the loop to let the model process the results and potentially make more calls
                    continue
                else:
                    # No more function calls - we have the final response
                    logger.info(f"Function calling completed after {iteration} iterations")
                    content = response.choices[0].message.content or "No response content"
                    break
            else:
                # Hit max iterations
                logger.warning(f"Function calling loop hit max iterations ({max_iterations})")
                content = "Function calling completed but may be incomplete due to complexity. Please try breaking down your request into smaller steps."
            
            return ModelResponse(
                content=content,
                model=model,
                confidence=0.85,
                reasoning=f"OpenAI response with Google Drive tools support (completed in {iteration} iterations)"
            )
            
        except Exception as e:
            logger.error(f"OpenAI API error with tools: {e}")
            return ModelResponse(
                content=f"Error getting OpenAI response: {str(e)}",
                model=model,
                confidence=0.0,
                reasoning="API error occurred"
            )

# Global orchestrator instance
llm_orchestrator = LLMOrchestrator()
