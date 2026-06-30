import asyncio
import logging
from datetime import datetime
from backend.config import config_manager
from backend.services.orchestrator import orchestrator

logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self):
        self.last_run_date = None
        self._task = None

    def start(self):
        """Start the background scheduler loop."""
        if self._task is None:
            self._task = asyncio.create_task(self._loop())
            logger.info("Internal scheduler started.")

    async def _loop(self):
        while True:
            try:
                config = config_manager.get_config()
                schedule_time_str = config.schedule_time.strip()
                
                if schedule_time_str:
                    now = datetime.now()
                    
                    # Try to parse the time (supports 08:00 AM or 08:00)
                    try:
                        target_time = datetime.strptime(schedule_time_str, "%I:%M %p").time()
                    except ValueError:
                        try:
                            target_time = datetime.strptime(schedule_time_str, "%H:%M").time()
                        except ValueError:
                            logger.error(f"Invalid schedule_time format: {schedule_time_str}. Expected 'HH:MM AM/PM' or 'HH:MM'.")
                            await asyncio.sleep(60)
                            continue

                    # Check if current time matches target hour and minute
                    if now.hour == target_time.hour and now.minute == target_time.minute:
                        # Ensure it only runs once per day
                        if self.last_run_date != now.date():
                            logger.info(f"Scheduler triggered for {schedule_time_str}")
                            self.last_run_date = now.date()
                            
                            # Run orchestrator in background without awaiting it to avoid blocking the scheduler loop
                            asyncio.create_task(orchestrator.run_all())
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
                
            # Check every 60 seconds
            await asyncio.sleep(60)

scheduler = Scheduler()

def setup_scheduler():
    scheduler.start()
