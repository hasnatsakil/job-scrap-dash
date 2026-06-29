import json, logging, httpx
from typing import Dict, Any
from pydantic import BaseModel
from backend.config import env_settings, config_manager

logger = logging.getLogger(__name__)

class AIProviderResult(BaseModel):
    keep: bool
    score: int
    reason: str

class AIProvider:
    def evaluate_job(self, job: Dict[str, Any], prompt: str, model: str) -> AIProviderResult: raise NotImplementedError

class OpenRouterProvider(AIProvider):
    async def evaluate_job_async(self, job: Dict[str, Any]) -> AIProviderResult:
        config = config_manager.get_config()
        system_content = f"{config.ai_system_prompt}\nReturn ONLY JSON: {{\"keep\": true/false, \"score\": 0-100, \"reason\": \"str\"}}"
        user_content = f"Title: {job.get('title')}\nCompany: {job.get('company')}\nLocation: {job.get('location')}\nType: {job.get('work_type')}\nDescription: {job.get('description')[:3000]}"
        headers = {"Authorization": f"Bearer {env_settings.openrouter_api_key}", "HTTP-Referer": "https://github.com/ai-job-scraper", "X-Title": "AI Job Scraper", "Content-Type": "application/json"}
        payload = {"model": config.ai_model, "response_format": {"type": "json_object"}, "messages": [{"role": "system", "content": system_content}, {"role": "user", "content": user_content}]}
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
                response.raise_for_status()
                result = json.loads(response.json()["choices"][0]["message"]["content"])
                return AIProviderResult(keep=bool(result.get("keep", False)), score=int(result.get("score", 0)), reason=str(result.get("reason", "No reason provided")))
        except Exception as e:
            logger.error(f"OpenRouter API Error: {e}")
            raise e

def get_ai_provider() -> OpenRouterProvider: return OpenRouterProvider()
