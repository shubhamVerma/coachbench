import os
import time
import yaml
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

from src.models import ModelName, Message, ModelResponse, QueryRequest

load_dotenv()


class ModelClient:
    """Unified interface for OpenRouter and DeepSeek APIs"""
    
    def __init__(self):
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        
        self.openrouter_base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        
        # Load model configurations
        with open("config/models.yaml", "r") as f:
            self.config = yaml.safe_load(f)
        
        if not self.openrouter_api_key or not self.deepseek_api_key:
            raise ValueError("Missing required API keys in environment variables")
        
        # Ensure API keys are strings
        self.openrouter_api_key = str(self.openrouter_api_key)
        self.deepseek_api_key = str(self.deepseek_api_key)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _make_request(
        self, 
        base_url: str, 
        api_key: str, 
        model: str, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: int = 1500
    ) -> tuple[Dict[str, Any], float]:
        """Make HTTP request to API with retry logic"""
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Add OpenRouter-specific headers if applicable
        if "openrouter" in base_url:
            headers["HTTP-Referer"] = "https://github.com/yourusername/coaching-llm-benchmark"
            headers["X-Title"] = "LLM Coaching Benchmark"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            response_time = (time.time() - start_time) * 1000
            
            return response.json(), response_time
    
    def _get_model_config(self, model_name: ModelName) -> Dict[str, Any]:
        """Get configuration for a specific model"""
        if model_name == ModelName.DEEPSEEK_V3:
            return self.config["models"]["deepseek"]
        else:
            return self.config["models"][model_name]
    
    async def query(
        self, 
        model_name: ModelName, 
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> ModelResponse:
        """Query any model with unified interface"""
        
        model_config = self._get_model_config(model_name)
        
        # Use provided parameters or fall back to config defaults
        temp = temperature or model_config.get("temperature", 0.7)
        tokens = max_tokens or model_config.get("max_tokens", 1500)
        
        # Convert Message objects to API format
        api_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        
        # Choose appropriate API
        if model_name == ModelName.DEEPSEEK_V3:
            base_url = self.deepseek_base_url
            api_key = self.deepseek_api_key
            model = model_config["model"]
        else:
            base_url = self.openrouter_base_url
            api_key = self.openrouter_api_key
            model = model_config["endpoint"]
        
        try:
            response_data, response_time = await self._make_request(
                base_url, api_key, model, api_messages, temp, tokens
            )
            
            content = response_data["choices"][0]["message"]["content"]
            usage = response_data.get("usage", {})
            
            return ModelResponse(
                model=model_name,
                content=content,
                usage=usage if isinstance(usage, dict) else {},
                response_time_ms=response_time
            )
            
        except Exception as e:
            print(f"Error querying {model_name}: {e}")
            raise
    
    async def query_batch(
        self,
        requests: List[QueryRequest]
    ) -> List[ModelResponse]:
        """Batch queries with rate limiting"""
        results = []
        
        for request in requests:
            try:
                response = await self.query(
                    request.model,
                    request.messages,
                    request.temperature,
                    request.max_tokens
                )
                results.append(response)
                
                # Rate limiting delay
                await asyncio.sleep(1.0)
                
            except Exception as e:
                print(f"Failed to process request for {request.model}: {e}")
                # Add a placeholder response or handle as needed
                continue
        
        return results
    
    @asynccontextmanager
    async def batch_context(self):
        """Context manager for batch operations"""
        yield self


# Global client instance
client = ModelClient()