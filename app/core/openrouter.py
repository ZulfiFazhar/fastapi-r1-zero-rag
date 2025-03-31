import httpx
import logging
from app.core.config import settings

class OpenRouterClient:
    """Client for interacting with OpenRouter API."""
    
    def __init__(self, api_key=None, base_url=None):
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        self.base_url = base_url or settings.OPENROUTER_API_URL
        
        if not self.api_key:
            logging.warning("OpenRouter API key not set")
    
    async def generate_embeddings(self, texts, model=None):
        """Generate embeddings for the provided texts."""
        if not isinstance(texts, list):
            texts = [texts]
            
        model = model or settings.EMBEDDING_MODEL
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    # "HTTP-Referer": "https://your-app-url.com",  # Replace with your app URL
                    "X-Title": settings.PROJECT_NAME
                },
                json={
                    "model": model,
                    "input": texts
                },
                timeout=60.0
            )
            
            if response.status_code != 200:
                logging.error(f"Error generating embeddings: {response.text}")
                response.raise_for_status()
                
            return response.json()
    
    async def generate_completion(self, messages, model=None, temperature=0.7, max_tokens=1000):
        """Generate a completion using the OpenRouter API."""
        model = model or settings.DEFAULT_LLM_MODEL
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    # "HTTP-Referer": "https://your-app-url.com",  # Replace with your app URL
                    "X-Title": settings.PROJECT_NAME
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                },
                timeout=60.0
            )
            
            if response.status_code != 200:
                logging.error(f"Error generating completion: {response.text}")
                response.raise_for_status()
                
            return response.json()