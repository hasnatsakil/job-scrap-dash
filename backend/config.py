import os
import json
from typing import Optional, List
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    port: int = Field(8000, alias="PORT")
    environment: str = Field("development", alias="ENVIRONMENT")
    google_sheets_credentials_b64: str = Field(..., alias="GOOGLE_SHEETS_CREDENTIALS_B64")
    google_sheet_id: str = Field(..., alias="GOOGLE_SHEET_ID")
    openrouter_api_key: str = Field(..., alias="OPENROUTER_API_KEY")
    linkedin_li_at_cookie: Optional[str] = Field(None, alias="LINKEDIN_LI_AT_COOKIE")

    # New variable for encrypting browser sessions
    session_encryption_key: str = Field("default_insecure_key_please_change_in_production", alias="SESSION_ENCRYPTION_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

try:
    env_settings = Settings()
except Exception:
    class MockSettings:
        port = 8000
        environment = "test"
        google_sheets_credentials_b64 = ""
        google_sheet_id = ""
        openrouter_api_key = ""
        linkedin_li_at_cookie = None
        session_encryption_key = "test_key"
    env_settings = MockSettings()

class AppConfigCache(BaseModel):
    schedule_time: str = "08:00 AM"
    ai_model: str = "openai/gpt-oss-20b:free"
    ai_system_prompt: str = "Evaluate if this job is a good fit."
    max_pages_per_source: int = 5
    max_jobs_per_keyword: int = 50
    delay_between_requests: int = 2
    retry_count: int = 3
    timeout: int = 30
    concurrency: int = 2
    ai_request_budget_daily: int = 100
    search_provider: str = "duckduckgo"
    enabled_sources: List[str] = ["linkedin", "greenhouse", "lever", "ashby"]
    search_keywords: List[str] = ["Python Developer", "Backend Engineer"]

class ConfigManager:
    _cache: Optional[AppConfigCache] = None

    @classmethod
    def get_config(cls) -> AppConfigCache:
        if cls._cache is None: return AppConfigCache()
        return cls._cache

    @classmethod
    def update_config(cls, new_config: AppConfigCache):
        cls._cache = new_config

config_manager = ConfigManager()
