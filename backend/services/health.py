from datetime import datetime
from backend.config import config_manager, env_settings
from backend.services.ai_manager import ai_manager

class HealthMonitor:
    def __init__(self):
        self.last_scrape_attempt, self.last_successful_scrape, self.scheduler_status = None, None, "Not Running"
    def record_attempt(self): self.last_scrape_attempt = datetime.now().isoformat()
    def record_success(self): self.last_successful_scrape = datetime.now().isoformat()
    def get_health_status(self):
        config = config_manager.get_config()
        return {"status": "ok", "scheduler_status": self.scheduler_status, "last_scrape_attempt": self.last_scrape_attempt, "last_successful_scrape": self.last_successful_scrape, "active_sources": len(config.enabled_sources), "active_keywords": len(config.search_keywords), "ai_budget_used": ai_manager.daily_requests_used, "ai_budget_total": config.ai_request_budget_daily, "google_sheets_configured": bool(env_settings.google_sheet_id and env_settings.google_sheets_credentials_b64)}

health_monitor = HealthMonitor()
