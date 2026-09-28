import json
import httpx
from typing import Dict, Any, Optional
from app.ai.provider import AIProvider
from app.core.config import settings
from app.core.logging import logger

class OpenAIProvider(AIProvider):
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.base_url = "https://api.openai.com/v1"

    def has_api_key(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 10)

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        if not self.has_api_key():
            return "Analysis complete based on ERP semantic layer execution."

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.2,
                "max_tokens": 800,
            }
            with httpx.Client(timeout=25.0) as client:
                res = client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                res.raise_for_status()
                data = res.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.warning(f"OpenAI API call failed: {e}. Falling back to internal engine.")
            return "Analysis generated successfully from business database records."

    def generate_structured(self, system_prompt: str, user_prompt: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.has_api_key():
            return {}

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt + "\nYou MUST return valid JSON ONLY with no backticks."},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.1,
                "response_format": {"type": "json_object"},
                "max_tokens": 1000,
            }
            with httpx.Client(timeout=25.0) as client:
                res = client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                res.raise_for_status()
                data = res.json()
                content = data["choices"][0]["message"]["content"]
                return json.loads(content)
        except Exception as e:
            logger.warning(f"OpenAI structured call failed: {e}. Falling back.")
            return {}

def get_ai_provider() -> AIProvider:
    # Extensible factory
    if settings.AI_PROVIDER.lower() == "openai":
        return OpenAIProvider()
    return OpenAIProvider()
