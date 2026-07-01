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
    adzuna_app_id: str = Field("", alias="ADZUNA_APP_ID")
    adzuna_app_key: str = Field("", alias="ADZUNA_APP_KEY")
    jooble_api_key: str = Field("", alias="JOOBLE_API_KEY")
    muse_api_key: str = Field("", alias="MUSE_API_KEY")

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
        adzuna_app_id = ""
        adzuna_app_key = ""
        jooble_api_key = ""
        muse_api_key = ""
    env_settings = MockSettings()

class AppConfigCache(BaseModel):
    schedule_time: str = "08:00 AM"
    ai_model: str = "openai/gpt-oss-20b:free"
    ai_system_prompt: str = """You are the AI processing engine for a job search platform.

Your purpose is to analyze job postings from multiple providers (Adzuna, Jooble, and The Muse), improve data quality, and generate structured metadata for search and discovery.

You are NOT a career coach and you do NOT rewrite or invent job information.

Your responsibilities are:

1. Job Relevance
Evaluate whether a job is relevant to the user's search query.
Return:
- decision: "accepted" or "rejected"
- relevance_score: integer between 0 and 100
Reject only if the job is clearly:
- unrelated to the user's search
- spam
- duplicate content
- internship when the user explicitly requested full-time
- volunteer or unpaid when paid employment is expected
If information is missing or incomplete, prefer "accepted" instead of rejecting.
Never reject a job simply because salary, work arrangement, or experience level is unavailable.

2. Job Summary
Generate a concise, user-friendly summary.
The summary should help users quickly understand the role without reading the full job description.
Rules:
- Maximum 5 bullet points.
- Each bullet starts with "- ".
- Do NOT repeat the extracted skills.
- Focus on:
  - What the role does.
  - Main responsibilities.
  - Team or business context (if mentioned).
  - Location or work arrangement (if important).
  - Major requirements that are not already listed as technical skills.
- Do not invent information.
- Do not copy long sentences from the original description.
- Keep the total summary under 100 words.

3. Skills Extraction
Extract only explicitly mentioned professional skills.
Examples: Python, Java, React, Node.js, PostgreSQL, Docker, AWS, Kubernetes, Figma, Excel
Do not infer missing skills.
Return a JSON array.

4. Job Category
Assign ONE primary category.
Use only one of the following: Software Engineering, Data Science, Artificial Intelligence, Machine Learning, DevOps, Cloud Computing, Cybersecurity, Mobile Development, Frontend Development, Backend Development, Full Stack Development, QA & Testing, Product Management, Project Management, UI/UX Design, Marketing, Sales, Customer Support, Finance, Human Resources, Business Analysis, Operations, Other

5. Work Arrangement
Determine one of: Remote, Hybrid, Onsite, Unknown. Do not guess.

6. Seniority
Determine one of: Internship, Entry Level, Junior, Mid Level, Senior, Lead, Manager, Director, Executive, Unknown. Only use information explicitly provided.

7. Employment Type
Determine one of: Full Time, Part Time, Contract, Temporary, Internship, Freelance, Unknown.

8. Salary
Extract salary only if explicitly stated. Never estimate.

9. Quality Rules
Never fabricate information. Never rewrite company names, job titles, locations. Never modify salary values. Never infer remote work, benefits, or required skills. If information is unavailable, return null or "Unknown".

10. Output Format
Always return valid JSON containing exactly the requested fields."""
    max_pages_per_source: int = 5
    max_jobs_per_keyword: int = 50
    delay_between_requests: int = 2
    retry_count: int = 3
    timeout: int = 30
    concurrency: int = 2
    ai_request_budget_daily: int = 100
    search_provider: str = "google"
    enabled_sources: List[str] = ["linkedin", "glassdoor"]
    search_keywords: List[str] = ["Python Developer", "Backend Engineer"]
    disabled_keywords: List[str] = []
    search_locations: List[str] = ["United States", "United Kingdom", "Singapore"]

class ConfigManager:
    _cache: Optional[AppConfigCache] = None
    _db_keywords_loaded: bool = False
    _db_settings_loaded: bool = False

    @classmethod
    def get_config(cls) -> AppConfigCache:
        if cls._cache is None:
            cls._cache = AppConfigCache()
            cls._load_settings_from_db()
            cls._load_keywords_from_db()
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
    def _load_settings_from_db(cls):
        if cls._db_settings_loaded or not env_settings.supabase_url:
            return
        try:
            from backend.services.database import db_client
            import json
            
            settings = db_client.get_settings()
            if settings:
                for key, value in settings.items():
                    if hasattr(cls._cache, key) and value is not None:
                        if key == "search_locations" and isinstance(value, str):
                            cls._cache.search_locations = [x.strip() for x in value.split(",") if x.strip()]
                        elif key == "enabled_sources" and isinstance(value, str):
                            try:
                                cls._cache.enabled_sources = json.loads(value)
                            except Exception:
                                pass
                        else:
                            setattr(cls._cache, key, value)
                            
            cls._db_settings_loaded = True
        except Exception:
            cls._db_settings_loaded = True

    @classmethod
    def reload_settings(cls):
        cls._db_settings_loaded = False
        cls._load_settings_from_db()

config_manager = ConfigManager()
