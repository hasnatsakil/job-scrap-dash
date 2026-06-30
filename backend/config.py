import os
import json
from typing import Optional, List
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    port: int = Field(8000, alias="PORT")
    supabase_url: str = Field(..., alias="SUPABASE_URL")
    supabase_key: str = Field(..., alias="SUPABASE_KEY")
    openrouter_api_key: str = Field(..., alias="OPENROUTER_API_KEY")

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
        supabase_url = ""
        supabase_key = ""
        openrouter_api_key = ""
    env_settings = MockSettings()

class AppConfigCache(BaseModel):
    schedule_time: str = "08:00 AM"
    ai_model: str = "openai/gpt-oss-20b:free"
    ai_system_prompt: str = """You are an expert technical recruiting assistant.

Your task is to evaluate whether a job posting matches the user's search keyword and should be kept.

Evaluation rules:

1. The job title should closely match the search keyword or be a reasonable variation.
2. The required skills, technologies, or responsibilities should be relevant to the keyword.
3. Ignore the location, work arrangement (remote, hybrid, onsite), salary, and years of experience unless they clearly make the job unrelated.
4. Accept jobs even if they are not a perfect match. Favor keeping potentially relevant jobs rather than rejecting them.
5. Reject only jobs that are clearly unrelated to the search keyword.
6. If there is insufficient information, prefer "accepted" rather than rejecting."""
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
    disabled_keywords: List[str] = []

class ConfigManager:
    _cache: Optional[AppConfigCache] = None
    _db_keywords_loaded: bool = False
    _db_sources_loaded: bool = False

    @classmethod
    def get_config(cls) -> AppConfigCache:
        if cls._cache is None:
            cls._cache = AppConfigCache()
            cls._load_keywords_from_db()
            cls._load_sources_from_db()
        return cls._cache

    @classmethod
    def update_config(cls, new_config: AppConfigCache):
        cls._cache = new_config

    @classmethod
    def _load_keywords_from_db(cls):
        if cls._db_keywords_loaded or not env_settings.supabase_url:
            return
        try:
            from backend.services.database import db_client
            rows = db_client.get_keywords()
            if rows:
                enabled = [r["keyword"] for r in rows if r.get("enabled")]
                disabled = [r["keyword"] for r in rows if not r.get("enabled")]
                if enabled:
                    cls._cache.search_keywords = enabled
                if disabled:
                    cls._cache.disabled_keywords = disabled
            cls._db_keywords_loaded = True
        except Exception:
            cls._db_keywords_loaded = True

    @classmethod
    def reload_keywords(cls):
        cls._db_keywords_loaded = False
        cls._load_keywords_from_db()

    @classmethod
    def _load_sources_from_db(cls):
        """Load enabled_sources from the Supabase sources table."""
        if cls._db_sources_loaded or not env_settings.supabase_url:
            return
        try:
            from backend.services.database import db_client
            rows = db_client.get_sources()
            if rows:
                enabled = [r["name"] for r in rows if r.get("enabled")]
                if enabled:
                    cls._cache.enabled_sources = enabled
            cls._db_sources_loaded = True
        except Exception:
            # Graceful fallback — keep the hardcoded default
            cls._db_sources_loaded = True

    @classmethod
    def reload_sources(cls):
        """Force a reload of sources from the database."""
        cls._db_sources_loaded = False
        cls._load_sources_from_db()

    @classmethod
    def sync_sources_to_db(cls):
        """Persist the current in-memory enabled_sources to Supabase."""
        if not cls._cache:
            return
        try:
            from backend.services.database import db_client
            all_known = ["linkedin", "greenhouse", "lever", "ashby"]
            rows = [
                {"name": s, "enabled": s in cls._cache.enabled_sources}
                for s in all_known
            ]
            db_client.upsert_all_sources(rows)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to sync sources to DB: {e}")

    @classmethod
    def sync_keywords_to_db(cls):
        try:
            from backend.services.database import db_client
            enabled_rows = [{"keyword": kw, "enabled": True} for kw in cls._cache.search_keywords]
            disabled_rows = [{"keyword": kw, "enabled": False} for kw in cls._cache.disabled_keywords]
            rows = enabled_rows + disabled_rows

            existing = db_client.get_keywords()
            existing_map = {r["keyword"]: r for r in existing}

            for row in rows:
                kw = row["keyword"]
                if kw in existing_map:
                    if existing_map[kw]["enabled"] != row["enabled"]:
                        db_client.update_keyword(existing_map[kw]["id"], {"enabled": row["enabled"]})
                else:
                    db_client.add_keyword(kw, row["enabled"])

            existing_keywords = {r["keyword"] for r in rows}
            for r in existing:
                if r["keyword"] not in existing_keywords:
                    db_client.delete_keyword(r["id"])
        except Exception:
            pass

config_manager = ConfigManager()
