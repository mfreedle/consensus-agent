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
            api_key=settings.openai_api_key,
            organization=settings.openai_org_id if settings.openai_org_id else None
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
        model: str = "gpt-4o-mini",
        context: Optional[str] = None
    ) -> ModelResponse:
        """Get response from OpenAI using Chat Completions API"""
        try:
            # Prepare messages with context if provided
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
            
            # Use OpenAI Chat Completions API
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            return ModelResponse(
                content=content,
                model=model,
                confidence=0.8,
                reasoning="OpenAI response"
            )
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return ModelResponse(
                content=f"Error getting OpenAI response: {str(e)}",
                model=model,
                confidence=0.0,
                reasoning="API error occurred"
            )
    
    async def get_grok_response(
        self, 
        prompt: str, 
        model: str = "grok-2",
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
        openai_model: str = "gpt-4o",
        grok_model: str = "grok-2"
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
        
        Format your response as a structured analysis.
        """
        
        try:
            consensus_response = await self.openai_client.responses.create(
                model=openai_model,
                instructions="You are an expert analyst that creates consensus from multiple AI responses. Be thorough and balanced in your analysis.",
                input=consensus_prompt,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "consensus_analysis",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "final_consensus": {"type": "string"},
                                "confidence_score": {"type": "number", "minimum": 0, "maximum": 1},
                                "reasoning": {"type": "string"},
                                "debate_points": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["final_consensus", "confidence_score", "reasoning", "debate_points"]
                        }
                    }
                }
            )
            
            consensus_data = consensus_response.output_parsed if hasattr(consensus_response, 'output_parsed') else {
                "final_consensus": "Unable to parse consensus response",
                "confidence_score": 0.5,
                "reasoning": "Parsing error",
                "debate_points": []
            }
            
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
