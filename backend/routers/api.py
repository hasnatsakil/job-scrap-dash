from fastapi import APIRouter, BackgroundTasks
from backend.services.health import health_monitor
from backend.services.google_sheet import google_sheets_service
from backend.config import config_manager, AppConfigCache

router = APIRouter()
from backend.routers.connections import router as connections_router
router.include_router(connections_router)

@router.get("/health")
async def health_check(): return await health_monitor.get_health_status()

@router.get("/jobs")
async def get_jobs(): return {"jobs": google_sheets_service.get_all_rows("Jobs")}

@router.get("/stats")
async def get_stats():
    rows = google_sheets_service.get_all_rows("Jobs")
    return {"total_found": len(rows), "ai_accepted": len([r for r in rows if r.get("AI Decision") == "Keep"]), "ai_rejected": len([r for r in rows if r.get("AI Decision") == "Reject"])}

@router.get("/settings")
async def get_settings(): return config_manager.get_config().model_dump()

@router.put("/settings")
async def update_settings(new_settings: AppConfigCache):
    config_manager.update_config(new_settings)
    return {"status": "success", "settings": new_settings.model_dump()}

@router.post("/run")
async def run_scraper(background_tasks: BackgroundTasks):
    # Replace with direct call or queue in Vercel
    pass
    return {"status": "started", "message": "Scraping job started in background"}
