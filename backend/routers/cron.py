from fastapi import APIRouter, Request, HTTPException
from backend.services.health import health_monitor
from backend.services.connection_manager import connection_manager
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/api/cron")
async def vercel_cron(request: Request):
    """
    Endpoint triggered by Vercel Cron.
    In a real scenario, you'd secure this with a secret header (CRON_SECRET).
    """
    logger.info("Vercel CRON job triggered")
    health_monitor.record_attempt()

    # 1. Validate sessions
    await connection_manager.validate_all()

    # 2. Scraping logic goes here

    health_monitor.record_success()
    return {"status": "ok"}
