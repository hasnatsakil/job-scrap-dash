from datetime import date
from typing import Dict
from fastapi import APIRouter, BackgroundTasks
from backend.services.health import health_monitor
from backend.services.database import db_client
from backend.config import config_manager, AppConfigCache

router = APIRouter()

@router.get("/health")
async def health_check(): return await health_monitor.get_health_status()

@router.get("/jobs")
async def get_jobs(): return {"jobs": db_client.get_all("jobs")}

@router.get("/logs")
async def get_logs(): return {"logs": db_client.get_all("logs")}

@router.get("/stats")
async def get_stats():
    rows = db_client.get_all("jobs")
    today_str = date.today().isoformat()
    today_count = len([r for r in rows if (r.get("scraped_at") or "").startswith(today_str)])
    return {"total_found": len(rows), "today": today_count, "ai_accepted": len([r for r in rows if r.get("ai_status") == "Keep"]), "ai_rejected": len([r for r in rows if r.get("ai_status") == "Reject"])}

@router.get("/settings")
async def get_settings(): return config_manager.get_config().model_dump()

@router.put("/settings")
async def update_settings(new_settings: AppConfigCache):
    config_manager.update_config(new_settings)
    return {"status": "success", "settings": new_settings.model_dump()}

from backend.services.orchestrator import orchestrator

@router.post("/run")
@router.post("/dispatch")
async def run_scraper(background_tasks: BackgroundTasks):
    background_tasks.add_task(orchestrator.run_all)
    return {"status": "started", "message": "Scraping job started in background"}

@router.get("/sources")
async def get_sources():
    config = config_manager.get_config()
    all_sources = ["adzuna", "jooble", "muse"]
    sources = []
    for i, s in enumerate(all_sources):
        sources.append({
            "id": i + 1,
            "name": s.capitalize(),
            "enabled": s in config.enabled_sources,
            "health": "ok" if s in config.enabled_sources else "gray",
            "delay": config.delay_between_requests,
            "retry": config.retry_count,
            "timeout": config.timeout,
            "jobs_collected": 0
        })
    return {"sources": sources}

@router.put("/sources/{source_name}/toggle")
async def toggle_source(source_name: str):
    config = config_manager.get_config()
    name_lower = source_name.lower()
    if name_lower in config.enabled_sources:
        config.enabled_sources.remove(name_lower)
        enabled = False
    else:
        config.enabled_sources.append(name_lower)
        enabled = True
    config_manager.update_config(config)
    config_manager.sync_sources_to_db()
    return {"status": "success", "enabled": enabled}

@router.get("/keywords")
async def get_keywords():
    db_rows = db_client.get_keywords()

    jobs = db_client.get_all("jobs")
    keyword_counts: Dict[str, int] = {}
    for job in jobs:
        kw = job.get("keyword")
        if kw:
            keyword_counts[kw] = keyword_counts.get(kw, 0) + 1

    logs = db_client.get_all("logs")
    keyword_last_search: Dict[str, str] = {}
    all_last_search = None
    for log in logs:
        kw = log.get("keyword")
        ts = log.get("time")
        if kw and ts:
            if kw == "All":
                if not all_last_search or ts > all_last_search:
                    all_last_search = ts
            else:
                if kw not in keyword_last_search or ts > keyword_last_search[kw]:
                    keyword_last_search[kw] = ts

    keywords_list = []
    for row in db_rows:
        kw = row["keyword"]
        keywords_list.append({
            "id": row["id"],
            "keyword": kw,
            "enabled": row["enabled"],
            "jobs_found": keyword_counts.get(kw, 0),
            "last_search": keyword_last_search.get(kw) or all_last_search
        })

    return {"keywords": keywords_list}

from pydantic import BaseModel
class KeywordCreate(BaseModel):
    keyword: str
    enabled: bool = True

class KeywordUpdate(BaseModel):
    keyword: str
    enabled: bool

@router.post("/keywords")
async def add_keyword(data: KeywordCreate):
    kw = data.keyword.strip()
    if not kw:
        return {"status": "error"}

    existing = db_client.get_keywords()
    if kw in [r["keyword"] for r in existing]:
        return {"status": "error", "message": "Keyword already exists"}

    row = db_client.add_keyword(kw, data.enabled)
    if row:
        config = config_manager.get_config()
        target_list = config.search_keywords if data.enabled else config.disabled_keywords
        if kw not in target_list:
            target_list.append(kw)
        config_manager.update_config(config)
        return {"status": "success"}
    return {"status": "error"}

@router.put("/keywords/{id}")
async def update_keyword(id: str, data: KeywordUpdate):
    config = config_manager.get_config()
    existing = db_client.get_keywords()
    target = next((r for r in existing if r["id"] == id), None)
    if not target:
        return {"status": "error", "message": "Keyword not found"}

    old_kw = target["keyword"]
    new_kw = data.keyword.strip() or old_kw

    if old_kw in config.search_keywords:
        config.search_keywords.remove(old_kw)
    if old_kw in config.disabled_keywords:
        config.disabled_keywords.remove(old_kw)

    target_list = config.search_keywords if data.enabled else config.disabled_keywords
    target_list.append(new_kw)
    config_manager.update_config(config)
    db_client.update_keyword(id, {"keyword": new_kw, "enabled": data.enabled})

    if new_kw != old_kw:
        db_client.update_jobs_keyword(old_kw, new_kw)

    return {"status": "success"}

@router.delete("/keywords/{id}")
async def delete_keyword(id: str):
    config = config_manager.get_config()
    existing = db_client.get_keywords()
    target = next((r for r in existing if r["id"] == id), None)
    if not target:
        return {"status": "error"}

    kw = target["keyword"]
    if kw in config.search_keywords:
        config.search_keywords.remove(kw)
    if kw in config.disabled_keywords:
        config.disabled_keywords.remove(kw)
    config_manager.update_config(config)
    db_client.delete_keyword(id)
    return {"status": "success"}



