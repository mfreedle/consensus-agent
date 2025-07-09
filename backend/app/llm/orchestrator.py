import asyncio
import logging
from typing import Any, Dict, List, Optional

import httpx
from app.config import settings
from openai import AsyncOpenAI, OpenAI
from pydantic import BaseModel

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
    
    def _supports_responses_api(self, model: str) -> bool:
        """Check if a model supports the Responses API with structured outputs"""
        # Only these models currently support Responses API with json_schema
        responses_api_models = ["gpt-4.1", "gpt-4.1-mini"]
        return model in responses_api_models

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
            if model in ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]:
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
            
            fallback_response = await self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=64000  # Increased for better responses
            )
            
            content = fallback_response.choices[0].message.content or "No response content"
            
            return ModelResponse(
                content=content,
                model=model,
                confidence=0.8,
                reasoning="Chat Completions API fallback"
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
        logger.info("Fetching responses from OpenAI and Grok in parallel...")
        openai_task = self.get_openai_response(prompt, openai_model, context)
        grok_task = self.get_grok_response(prompt, grok_model, context)
        
        openai_response, grok_response = await asyncio.gather(openai_task, grok_task)
        
        logger.info(f"OpenAI response confidence: {openai_response.confidence}")
        logger.info(f"Grok response confidence: {grok_response.confidence}")
        
        # Check if both responses are valid
        both_valid = (openai_response.confidence > 0 and grok_response.confidence > 0)
        
        # Enhanced consensus generation with debate simulation
        if both_valid:
            consensus_prompt = f"""
            You are an expert analyst creating consensus from multiple AI responses. Analyze these responses and create a comprehensive consensus.
            
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
            You are an expert analyst. One AI response is available for the user's question.
            
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

# Global orchestrator instance
llm_orchestrator = LLMOrchestrator()
