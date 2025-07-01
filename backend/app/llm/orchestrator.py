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
    
    async def get_openai_response(
        self, 
        prompt: str, 
        model: str = "gpt-4.1",  # Updated to use curated model
        context: Optional[str] = None
    ) -> ModelResponse:
        """Get response from OpenAI using Responses API with structured outputs"""
        try:
            # Prepare the input messages
            input_messages = []
            if context:
                input_messages.append({
                    "role": "system",
                    "content": f"Context: {context}\n\nYou are a helpful AI assistant. Provide thoughtful, accurate responses."
                })
            input_messages.append({
                "role": "user", 
                "content": prompt
            })
            
            # Use the new Responses API with structured outputs
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
            response_text = response.output[0].content[0].text
            response_data = json.loads(response_text)
            
            return ModelResponse(
                content=response_data["content"],
                model=model,
                confidence=response_data["confidence"],
                reasoning=response_data["reasoning"]
            )
            
        except Exception as e:
            logger.error(f"OpenAI Responses API error: {e}")
            # Fallback to regular chat completions if Responses API fails
            try:
                # Prepare messages for fallback
                messages = []
                if context:
                    messages.append({
                        "role": "system",
                        "content": f"Context: {context}\n\nYou are a helpful AI assistant. Provide thoughtful, accurate responses."
                    })
                messages.append({
                    "role": "user", 
                    "content": prompt
                })
                
                fallback_response = await self.openai_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                content = fallback_response.choices[0].message.content
                
                return ModelResponse(
                    content=content,
                    model=model,
                    confidence=0.8,
                    reasoning="Fallback to Chat Completions API"
                )
                
            except Exception as fallback_error:
                logger.error(f"Fallback OpenAI API error: {fallback_error}")
                return ModelResponse(
                    content=f"Error getting OpenAI response: {str(e)}",
                    model=model,
                    confidence=0.0,
                    reasoning="API error occurred"
                )
    
    async def get_grok_response(
        self, 
        prompt: str, 
        model: str = "grok-3-latest",  # Updated to use curated model
        context: Optional[str] = None
    ) -> ModelResponse:
        """Get response from Grok using xAI API"""
        try:
            # Prepare messages with context if provided
            messages = []
            if context:
                messages.append({"role": "system", "content": f"Context: {context}"})
            
            messages.append({"role": "user", "content": prompt})
            
            # Make request to Grok API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.grok_base_url}/chat/completions",
                    headers=self.grok_headers,
                    json={
                        "model": model,
                        "messages": messages,
                        "stream": False,
                        "temperature": 0.7
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
        openai_model: str = "gpt-4.1",        # Updated to use curated model
        grok_model: str = "grok-3-latest"     # Updated to use curated model
    ) -> ConsensusResult:
        """Generate consensus response from multiple models"""
        
        # Get responses from both models in parallel
        openai_task = self.get_openai_response(prompt, openai_model, context)
        grok_task = self.get_grok_response(prompt, grok_model, context)
        
        openai_response, grok_response = await asyncio.gather(openai_task, grok_task)
        
        # Generate consensus using OpenAI
        consensus_prompt = f"""
        You have two AI responses to the user's question. Your job is to create a consensus response that combines the best aspects of both.
        
        User Question: {prompt}
        
        OpenAI Response: {openai_response.content}
        Grok Response: {grok_response.content}
        
        Please create a consensus response that:
        1. Combines the best insights from both responses
        2. Resolves any contradictions
        3. Provides a confidence score (0-1)
        4. Explains your reasoning
        5. Lists key debate points if any disagreements exist
        
        Provide your response in the following JSON format:
        {{
            "final_consensus": "your consensus response here",
            "confidence_score": 0.85,
            "reasoning": "explanation of your analysis",
            "debate_points": ["point1", "point2", "point3"]
        }}
        """
        
        try:
            # Use O3 as the manager/judge model for consensus generation
            consensus_response = await self.openai_client.chat.completions.create(
                model="o3",  # Manager/judge model is always O3
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert analyst that creates consensus from multiple AI responses. Always respond with valid JSON in the requested format."
                    },
                    {
                        "role": "user", 
                        "content": consensus_prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            
            import json
            consensus_data = json.loads(consensus_response.choices[0].message.content)
            
            return ConsensusResult(
                openai_response=openai_response,
                grok_response=grok_response,
                final_consensus=consensus_data.get("final_consensus", ""),
                confidence_score=consensus_data.get("confidence_score", 0.5),
                reasoning=consensus_data.get("reasoning", ""),
                debate_points=consensus_data.get("debate_points", [])
            )
            
        except Exception as e:
            logger.error(f"Consensus generation error: {e}")
            # Fallback: simple combination
            return ConsensusResult(
                openai_response=openai_response,
                grok_response=grok_response,
                final_consensus=f"Combined response:\n\nOpenAI: {openai_response.content}\n\nGrok: {grok_response.content}",
                confidence_score=0.6,
                reasoning="Fallback consensus due to processing error",
                debate_points=["Unable to generate detailed analysis"]
            )

# Global orchestrator instance
llm_orchestrator = LLMOrchestrator()
