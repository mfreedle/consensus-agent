"""
LLM Orchestrator for handling multi-model consensus
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import httpx
from app.config import settings
from openai import AsyncOpenAI
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class LLMResponse(BaseModel):
    content: str
    confidence: float
    reasoning: str
    model: str
    provider: str

class ConsensusResult(BaseModel):
    openai_response: LLMResponse
    grok_response: LLMResponse
    final_consensus: str
    confidence_score: float
    reasoning: str
    debate_points: List[str]

class LLMOrchestrator:
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.grok_api_key = settings.grok_api_key
        
    async def get_openai_response(
        self, 
        prompt: str, 
        model: str = "gpt-4.1",
        context: Optional[str] = None
    ) -> LLMResponse:
        """Get response from OpenAI using the Responses API"""
        
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")
            
        try:
            # Prepare the input messages for the Responses API
            input_messages = []
            if context:
                input_messages.append({
                    "role": "system",
                    "content": f"Context: {context}\n\nYou are a helpful AI assistant. Provide clear, accurate responses with confidence scoring."
                })
            input_messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Use the new Responses API with structured output
            response = await self.openai_client.responses.create(
                model=model,
                input=input_messages,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "structured_response",
                        "description": "Structured response with confidence and reasoning",
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
                                    "description": "Confidence score from 0 to 1"
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
            
            return LLMResponse(
                content=response_data.get("content", "No response generated"),
                confidence=response_data.get("confidence", 0.5),
                reasoning=response_data.get("reasoning", "No reasoning provided"),
                model=model,
                provider="openai"
            )
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return LLMResponse(
                content=f"Error getting OpenAI response: {str(e)}",
                confidence=0.0,
                reasoning="API error occurred",
                model=model,
                provider="openai"
            )
    
    async def get_grok_response(
        self, 
        prompt: str, 
        model: str = "grok-3",
        context: Optional[str] = None
    ) -> LLMResponse:
        """Get response from Grok via xAI API"""
        
        if not self.grok_api_key:
            raise ValueError("Grok API key not configured")
            
        try:
            # Prepare the input with context if provided
            full_input = prompt
            if context:
                full_input = f"Context: {context}\n\nUser Query: {prompt}"
            
            headers = {
                "Authorization": f"Bearer {self.grok_api_key}",
                "Content-Type": "application/json"
            }
            
            # Grok API payload
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are Grok, a witty and intelligent AI assistant. Provide helpful responses with your characteristic humor and real-time knowledge."
                    },
                    {
                        "role": "user", 
                        "content": full_input
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    raise Exception(f"Grok API returned status {response.status_code}: {response.text}")
                
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                # Estimate confidence based on response length and coherence
                confidence = min(0.9, len(content.split()) / 100 + 0.5)
                
                return LLMResponse(
                    content=content,
                    confidence=confidence,
                    reasoning="Grok response with real-time knowledge and humor",
                    model=model,
                    provider="grok"
                )
                
        except Exception as e:
            logger.error(f"Grok API error: {e}")
            return LLMResponse(
                content=f"Error getting Grok response: {str(e)}",
                confidence=0.0,
                reasoning="API error occurred",
                model=model,
                provider="grok"
            )
    
    async def generate_consensus(
        self,
        prompt: str,
        context: Optional[str] = None,
        openai_model: str = "gpt-4.1",
        grok_model: str = "grok-3"
    ) -> ConsensusResult:
        """Generate consensus from multiple LLM responses"""
        
        try:
            # Get responses from both models in parallel
            openai_task = self.get_openai_response(prompt, openai_model, context)
            grok_task = self.get_grok_response(prompt, grok_model, context)
            
            openai_response, grok_response = await asyncio.gather(
                openai_task, grok_task, return_exceptions=True
            )
            
            # Handle potential exceptions
            if isinstance(openai_response, Exception):
                openai_response = LLMResponse(
                    content="OpenAI unavailable",
                    confidence=0.0,
                    reasoning="Service unavailable",
                    model=openai_model,
                    provider="openai"
                )
            
            if isinstance(grok_response, Exception):
                grok_response = LLMResponse(
                    content="Grok unavailable", 
                    confidence=0.0,
                    reasoning="Service unavailable",
                    model=grok_model,
                    provider="grok"
                )
            
            # Generate consensus
            consensus = await self._generate_consensus_analysis(
                openai_response, grok_response, prompt
            )
            
            return consensus
            
        except Exception as e:
            logger.error(f"Consensus generation error: {e}")
            # Fallback to single model response
            try:
                openai_response = await self.get_openai_response(prompt, openai_model, context)
                return ConsensusResult(
                    openai_response=openai_response,
                    grok_response=LLMResponse(
                        content="Unavailable",
                        confidence=0.0,
                        reasoning="Service unavailable",
                        model=grok_model,
                        provider="grok"
                    ),
                    final_consensus=openai_response.content,
                    confidence_score=openai_response.confidence,
                    reasoning="Single model fallback due to consensus error",
                    debate_points=[]
                )
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {fallback_error}")
                raise Exception("All LLM services unavailable")
    
    async def _generate_consensus_analysis(
        self,
        openai_response: LLMResponse,
        grok_response: LLMResponse,
        original_prompt: str
    ) -> ConsensusResult:
        """Analyze responses and generate consensus"""
        
        # Simple consensus logic
        responses = [openai_response, grok_response]
        valid_responses = [r for r in responses if r.confidence > 0.1]
        
        if not valid_responses:
            return ConsensusResult(
                openai_response=openai_response,
                grok_response=grok_response,
                final_consensus="I apologize, but I'm unable to provide a reliable response at this time.",
                confidence_score=0.0,
                reasoning="No valid responses from any model",
                debate_points=[]
            )
        
        # If only one valid response, use it
        if len(valid_responses) == 1:
            best_response = valid_responses[0]
            return ConsensusResult(
                openai_response=openai_response,
                grok_response=grok_response,
                final_consensus=best_response.content,
                confidence_score=best_response.confidence,
                reasoning=f"Single valid response from {best_response.provider}",
                debate_points=[f"Only {best_response.provider} provided a valid response"]
            )
        
        # Multiple valid responses - generate consensus
        avg_confidence = sum(r.confidence for r in valid_responses) / len(valid_responses)
        
        # Simple consensus: prefer higher confidence response but mention both
        best_response = max(valid_responses, key=lambda r: r.confidence)
        other_responses = [r for r in valid_responses if r != best_response]
        
        consensus_content = best_response.content
        if other_responses:
            other_content = other_responses[0].content
            if len(other_content) > 100 and other_content.lower() != consensus_content.lower():
                consensus_content += f"\n\nAlternative perspective: {other_content[:200]}..."
        
        debate_points = [
            f"OpenAI (confidence: {openai_response.confidence:.2f}): {openai_response.reasoning}",
            f"Grok (confidence: {grok_response.confidence:.2f}): {grok_response.reasoning}"
        ]
        
        return ConsensusResult(
            openai_response=openai_response,
            grok_response=grok_response,
            final_consensus=consensus_content,
            confidence_score=avg_confidence,
            reasoning=f"Consensus based on {len(valid_responses)} valid responses",
            debate_points=debate_points
        )

# Global orchestrator instance
llm_orchestrator = LLMOrchestrator()
