import json, logging, httpx
from typing import Dict, Any
from pydantic import BaseModel
from backend.config import env_settings, config_manager

logger = logging.getLogger(__name__)

class AIProviderResult(BaseModel):
    decision: str
    relevance_score: int
    category: str
    summary: str
    skills: list
    work_arrangement: str
    seniority: str
    employment_type: str
    salary: str
    reason: str

class AIProvider:
    def evaluate_job(self, job: Dict[str, Any], prompt: str, model: str) -> AIProviderResult: raise NotImplementedError

class OpenRouterProvider(AIProvider):
    async def evaluate_job_async(self, job: Dict[str, Any]) -> AIProviderResult:
        config = config_manager.get_config()
        model = config.ai_model

        # Enforce that only free models are allowed if OpenRouter is used
        if ":free" not in model.lower():
            logger.warning(f"Enforcing free model usage. Swapping {model} to openai/gpt-oss-20b:free")
            model = "openai/gpt-oss-20b:free"

        system_content = f"{config.ai_system_prompt}\nReturn only valid JSON in this format:\n{{\n  \"decision\": \"accepted\" | \"rejected\",\n  \"relevance_score\": 0-100,\n  \"category\": \"Job Category\",\n  \"summary\": \"- Bullet 1\\n- Bullet 2\",\n  \"skills\": [\"Skill 1\", \"Skill 2\"],\n  \"work_arrangement\": \"Remote/Hybrid/Onsite/Unknown\",\n  \"seniority\": \"Seniority level or Unknown\",\n  \"employment_type\": \"Type or Unknown\",\n  \"salary\": \"Salary or Unknown\",\n  \"reason\": \"Brief explanation\"\n}}"
        user_content = f"Search Keyword: {job.get('keyword', 'Unknown')}\nTitle: {job.get('title')}\nCompany: {job.get('company')}\nLocation: {job.get('location')}\nType: {job.get('work_type')}\nDescription: {job.get('description')[:3000]}"
        headers = {"Authorization": f"Bearer {env_settings.openrouter_api_key}", "HTTP-Referer": "https://github.com/ai-job-scraper", "X-Title": "AI Job Scraper", "Content-Type": "application/json"}
        payload = {"model": model, "response_format": {"type": "json_object"}, "messages": [{"role": "system", "content": system_content}, {"role": "user", "content": user_content}]}
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"]
                if content is None:
                    raise ValueError("API returned None content")
                result = json.loads(content)
                return AIProviderResult(
                    decision=str(result.get("decision", "rejected")),
                    relevance_score=int(result.get("relevance_score", 0)),
                    category=str(result.get("category", "Unknown")),
                    summary=str(result.get("summary", "")),
                    skills=result.get("skills", []),
                    work_arrangement=str(result.get("work_arrangement", "Unknown")),
                    seniority=str(result.get("seniority", "Unknown")),
                    employment_type=str(result.get("employment_type", "Unknown")),
                    salary=str(result.get("salary", "Unknown")),
                    reason=str(result.get("reason", "No reason provided"))
                )
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"OpenRouter JSON Parse Error: {e}")
            return AIProviderResult(decision="accepted", relevance_score=50, category="Unknown", summary="", skills=[], work_arrangement="Unknown", seniority="Unknown", employment_type="Unknown", salary="Unknown", reason="AI parse error, defaulting to accepted.")
        except Exception as e:
            logger.error(f"OpenRouter API Error: {e}")
            raise e

def get_ai_provider() -> OpenRouterProvider: return OpenRouterProvider()
