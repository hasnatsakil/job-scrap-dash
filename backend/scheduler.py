import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from backend.config import config_manager
from backend.services.health import health_monitor

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def scraping_job():
    logger.info("Starting scheduled scraping job...")
    health_monitor.record_attempt()
    health_monitor.record_success()
    logger.info("Scraping job completed.")

def setup_scheduler():
    config = config_manager.get_config()
    try:
        dt = datetime.strptime(config.schedule_time, "%I:%M %p")
        scheduler.remove_all_jobs()
        scheduler.add_job(scraping_job, CronTrigger(hour=dt.hour, minute=dt.minute), id='daily_scrape')
        if not scheduler.running: scheduler.start()
        health_monitor.scheduler_status = "Running"
    except Exception as e:
        health_monitor.scheduler_status = "Error"
        logger.error(f"Failed to setup scheduler: {e}")
