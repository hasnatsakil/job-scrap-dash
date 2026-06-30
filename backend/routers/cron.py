from fastapi import APIRouter, Request, BackgroundTasks
import logging

from backend.services.connection_manager import connection_manager
from backend.services.orchestrator import orchestrator

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/api/cron")
async def vercel_cron(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint triggered by Vercel Cron.
    In a real scenario, you'd secure this with a secret header (CRON_SECRET).
    """
    logger.info("Vercel CRON job triggered")
    
    # 1. Validate sessions (quick)
    await connection_manager.validate_all()

    # 2. Add full orchestrator run to background task
    background_tasks.add_task(orchestrator.run_all)
    
    return {"status": "ok", "message": "Cron scrape job scheduled in background."}
