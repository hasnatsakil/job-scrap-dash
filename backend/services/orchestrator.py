import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any

from playwright.async_api import async_playwright
from backend.config import config_manager
from backend.services.health import health_monitor
from backend.services.database import db_client
from backend.services.deduplicator import Deduplicator
from backend.services.ai_manager import ai_manager
from backend.services.captcha_detector import CaptchaDetectedException
from backend.services.job_hydrator import job_hydrator
from backend.services.content_extractor import content_extractor
from backend.services.content_cleaner import content_cleaner
from backend.services.content_validator import content_validator
from backend.services.normalizer import DataNormalizer

# Import scrapers
from backend.scrapers.linkedin import LinkedInScraper
from backend.scrapers.google import LeverScraper, GreenhouseScraper, AshbyScraper

logger = logging.getLogger(__name__)

SCRAPER_REGISTRY = {
    "linkedin": LinkedInScraper,
    "lever": LeverScraper,
    "greenhouse": GreenhouseScraper,
    "ashby": AshbyScraper
}

class Orchestrator:
    def __init__(self):
        self.is_running = False

    async def run_all(self):
        if self.is_running:
            logger.warning("Scraper is already running. Skipping this run.")
            return

        self.is_running = True
        health_monitor.record_attempt()
        health_monitor.scheduler_status = "Running"
        health_monitor.captcha_blocked_sources = []
        logger.info("Starting orchestrated scraper run.")

        try:
            config_manager.reload_keywords()
            config_manager.reload_sources()
            config = config_manager.get_config()
            if not config.enabled_sources or not config.search_keywords:
                logger.warning("No enabled sources or keywords found. Aborting.")
                return

            # Initialize deduplicator with existing jobs
            existing_jobs = db_client.get_all("jobs")
            dedup = Deduplicator(existing_jobs)
            
            total_collected = 0
            total_saved = 0
            start_time = datetime.now()
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                
                # We limit concurrency here loosely by iterating sources and keywords. 
                # A more advanced version would use asyncio.gather with a semaphore.
                for source_name in config.enabled_sources:
                    if source_name not in SCRAPER_REGISTRY:
                        logger.warning(f"No scraper registered for {source_name}")
                        continue
                        
                    scraper_cls = SCRAPER_REGISTRY[source_name]
                    
                    for keyword in config.search_keywords:
                        keyword_collected = 0
                        keyword_saved = 0
                        logger.info(f"Scraping {source_name} for '{keyword}'")
                        scraper = scraper_cls()
                        context = await browser.new_context()
                        
                        try:
                            jobs = await scraper.scrape(context, keyword)
                            keyword_collected = len(jobs)
                            unique_jobs = [job for job in jobs if not dedup.is_duplicate(job)]
                            
                            if unique_jobs:
                                # Add keyword to jobs so the AI has context for evaluation
                                for j in unique_jobs:
                                    j["keyword"] = keyword

                                # Hydrate the jobs (fetch raw html)
                                hydrated_jobs = await job_hydrator.hydrate_batch(context, unique_jobs)
                                
                                # Extract, Normalize, Clean, and Validate
                                extracted_jobs = [content_extractor.extract(job) for job in hydrated_jobs]
                                normalized_jobs = [DataNormalizer.normalize_job(job) for job in extracted_jobs]
                                cleaned_jobs = [content_cleaner.clean(job) for job in normalized_jobs]
                                validated_jobs = content_validator.validate_batch(cleaned_jobs)
                                
                                # Separate valid jobs for AI vs invalid jobs that skip AI
                                ai_batch = [j for j in validated_jobs if j.get("AI Decision") != "Reject"]
                                invalid_batch = [j for j in validated_jobs if j.get("AI Decision") == "Reject"]
                                
                                # Process in batches of 5 concurrently for AI evaluation
                                evaluated_batch = []
                                BATCH_SIZE = 5
                                for i in range(0, len(ai_batch), BATCH_SIZE):
                                    batch = ai_batch[i:i+BATCH_SIZE]
                                    tasks = [ai_manager.evaluate_job(j) for j in batch]
                                    evaluated_batch.extend(await asyncio.gather(*tasks, return_exceptions=False))
                                    
                                # Combine back with invalid jobs
                                final_batch = evaluated_batch + invalid_batch
                                
                                rows = self._format_jobs_for_db(final_batch, keyword)
                                db_client.insert("jobs", rows)
                                keyword_saved += len(final_batch)
                                logger.info(f"Saved {len(final_batch)} new jobs to database from {source_name}.")
                                    
                                # Add back to dedup to avoid duplicates across sources in the same run
                                for evaluated in final_batch:
                                    url = evaluated.get("job_url")
                                    if url:
                                        dedup.existing_urls.add(url.strip())
                                    company = evaluated.get("company", "").strip().lower()
                                    title = evaluated.get("title", "").strip().lower()
                                    if company and title:
                                        dedup.existing_signatures.add(f"{company}::{title}")

                            total_collected += keyword_collected
                            total_saved += keyword_saved
                        except CaptchaDetectedException as e:
                            logger.warning(f"CAPTCHA detected for {source_name}. Skipping remaining keywords for this source.")
                            health_monitor.record_captcha(source_name)
                            
                            log_row = {
                                "time": datetime.now().isoformat(),
                                "source": source_name,
                                "keyword": keyword,
                                "jobs_found": 0,
                                "message": f"CAPTCHA detected for {source_name} while scraping '{keyword}'. Skipping remaining keywords.",
                                "status": "warning"
                            }
                            db_client.insert("logs", [log_row])

                            await context.close()
                            break
                        except Exception as e:
                            logger.error(f"Failed to scrape {source_name} for '{keyword}': {e}")
                        finally:
                            if not context.is_closed():
                                await context.close()

                        # Log per-keyword result
                        db_client.insert("logs", [{
                            "time": datetime.now().isoformat(),
                            "source": source_name,
                            "keyword": keyword,
                            "jobs_found": keyword_collected,
                            "message": f"Scraped {keyword_collected} jobs, saved {keyword_saved} new from {source_name}",
                            "status": "success" if keyword_saved > 0 else "info"
                        }])
                            
                        await asyncio.sleep(config.delay_between_requests)

                await browser.close()
            
            duration = str(datetime.now() - start_time)
            
            # Save a log entry
            log_row = {
                "time": datetime.now().isoformat(),
                "source": "All",
                "keyword": "All",
                "jobs_found": total_collected,
                "message": f"Scraped {total_collected} jobs, saved {total_saved} new in {duration}",
                "status": "success"
            }
            db_client.insert("logs", [log_row])

            health_monitor.record_success()

        except Exception as e:
            logger.error(f"Orchestrator failed: {e}")
            log_row = {"time": datetime.now().isoformat(), "source": "All", "keyword": "All", "jobs_found": 0, "message": f"Orchestrator failed: {e}", "status": "error"}
            db_client.insert("logs", [log_row])
        finally:
            self.is_running = False
            health_monitor.scheduler_status = "Not Running"
            logger.info("Orchestrated scraper run completed.")

    def _format_jobs_for_db(self, jobs: List[Dict[str, Any]], keyword: str = "") -> List[Dict[str, Any]]:
        rows = []
        date_str = datetime.now().isoformat()
        for j in jobs:
            rows.append({
                "title": j.get("title", ""),
                "company": j.get("company", ""),
                "location": j.get("location", ""),
                "source": j.get("source", ""),
                "work_type": j.get("work_type", ""),
                "posted_date": None,
                "description": j.get("description", ""),
                "job_url": j.get("job_url", ""),
                "ai_score": j.get("AI Score") or 0,
                "ai_status": j.get("AI Decision", "Pending"),
                "keyword": keyword,
                "scraped_at": date_str,
            })
        return rows

orchestrator = Orchestrator()
