from datetime import datetime
from backend.config import config_manager, env_settings
from backend.services.ai_manager import ai_manager

class HealthMonitor:
    def __init__(self):
        self.last_scrape_attempt, self.last_successful_scrape, self.scheduler_status = None, None, "Not Running"
        self.total_runs = 0
        self.successful_runs = 0
        self.captcha_blocked_sources: List[str] = []

    def record_attempt(self): self.last_scrape_attempt = datetime.now().isoformat()

    def record_success(self):
        self.last_successful_scrape = datetime.now().isoformat()
        self.total_runs += 1
        self.successful_runs += 1

    def record_captcha(self, source: str):
        if source not in self.captcha_blocked_sources:
            self.captcha_blocked_sources.append(source)

    async def get_health_status(self):
        config = config_manager.get_config()
        return {
            "status": "ok",
            "scheduler_status": self.scheduler_status,
            "last_scrape_attempt": self.last_scrape_attempt,
            "last_successful_scrape": self.last_successful_scrape,
            "active_sources": len(config.enabled_sources),
            "enabled_sources": config.enabled_sources,
            "active_keywords": len(config.search_keywords),
            "ai_budget_used": ai_manager.daily_requests_used,
            "ai_budget_total": config.ai_request_budget_daily,
            "captcha_blocked_sources": self.captcha_blocked_sources,
            "database_configured": bool(env_settings.supabase_url and env_settings.supabase_key)
        }
health_monitor = HealthMonitor()
