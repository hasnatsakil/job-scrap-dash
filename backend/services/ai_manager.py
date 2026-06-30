import logging
from typing import Dict, Any
from datetime import datetime
from backend.services.ai_provider import get_ai_provider, AIProviderResult
from backend.config import config_manager

logger = logging.getLogger(__name__)

class AIManager:
    def __init__(self):
        self.provider = get_ai_provider()
        self.daily_requests_used = 0
        self.last_reset_date = datetime.now().date()

    def _check_budget(self) -> bool:
        current_date = datetime.now().date()
        if current_date != self.last_reset_date:
            self.daily_requests_used = 0
            self.last_reset_date = current_date
        return self.daily_requests_used < config_manager.get_config().ai_request_budget_daily

    async def evaluate_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        if not self._check_budget(): return self._mark_pending(job, "AI budget exceeded")
        try:
            result: AIProviderResult = await self.provider.evaluate_job_async(job)
            self.daily_requests_used += 1
            ai_decision = "Keep" if result.decision.lower() == "accepted" else "Reject"
            job["AI Score"], job["AI Decision"], job["AI Reason"] = result.score, ai_decision, result.reason
            return job
        except Exception as e: return self._mark_pending(job, f"AI Error: {str(e)}")

    def _mark_pending(self, job: Dict[str, Any], reason: str) -> Dict[str, Any]:
        job["AI Score"], job["AI Decision"], job["AI Reason"] = 0, "Pending AI Review", reason
        return job

ai_manager = AIManager()
