import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any

from backend.config import config_manager
from backend.services.health import health_monitor
from backend.services.database import db_client
from backend.services.deduplicator import Deduplicator
from backend.services.ai_manager import ai_manager
from backend.services.content_validator import content_validator
from backend.services.normalizer import DataNormalizer
from backend.services.query_expansion import query_expansion

# Import API Clients
from backend.apis.adzuna import AdzunaAPI
from backend.apis.jooble import JoobleAPI
from backend.apis.muse import MuseAPI
from backend.apis.google_scraper import LinkedInScraper, GlassdoorScraper

logger = logging.getLogger(__name__)

API_REGISTRY = {
    "adzuna": AdzunaAPI,
    "jooble": JoobleAPI,
    "muse": MuseAPI,
    "linkedin": LinkedInScraper,
    "glassdoor": GlassdoorScraper
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
        logger.info("Starting orchestrated API fetch run.")

        try:
            config_manager.reload_keywords()
            config_manager.reload_settings()
            config = config_manager.get_config()
            if not config.search_keywords:
                logger.warning("No search keywords found. Aborting.")
                return

            fallback_chain = ["adzuna", "jooble", "muse"]
            # Append web scrapers only if they are explicitly selected in settings
            for src in ["linkedin", "glassdoor"]:
                if config.enabled_sources and src in config.enabled_sources:
                    fallback_chain.append(src)

            existing_jobs = db_client.get_all("jobs")
            dedup = Deduplicator(existing_jobs)
            
            total_collected = 0
            total_saved = 0
            start_time = datetime.now()
            
            for location in config.search_locations:
                for keyword in config.search_keywords:
                    expanded_keywords = await query_expansion.expand(keyword)
                    keyword_saved_total = 0
                    
                    for source_name in fallback_chain:
                        if source_name not in API_REGISTRY:
                            logger.warning(f"No API client registered for {source_name}")
                            continue
                            
                        api_cls = API_REGISTRY[source_name]
                        api_client = api_cls()
                        
                        source_saved_total = 0
                        
                        for exp_kw in expanded_keywords:
                            logger.info(f"Fetching {source_name} for '{exp_kw}' in '{location}' (Original: {keyword})")
                            
                            try:
                                jobs = await api_client.fetch_jobs(exp_kw, location, limit=config.max_jobs_per_keyword)
                                keyword_collected = len(jobs)
                                total_collected += keyword_collected
                                
                                unique_jobs = [job for job in jobs if not dedup.is_duplicate(job)]
                                
                                if unique_jobs:
                                    for j in unique_jobs:
                                        j["keyword"] = keyword # Map back to original keyword

                                    normalized_jobs = [DataNormalizer.normalize_job(job) for job in unique_jobs]
                                    validated_jobs = content_validator.validate_batch(normalized_jobs)
                                    
                                    ai_batch = [j for j in validated_jobs if j.get("AI Decision") != "Reject"]
                                    invalid_batch = [j for j in validated_jobs if j.get("AI Decision") == "Reject"]
                                    
                                    evaluated_batch = []
                                    BATCH_SIZE = 5
                                    for i in range(0, len(ai_batch), BATCH_SIZE):
                                        batch = ai_batch[i:i+BATCH_SIZE]
                                        tasks = [ai_manager.evaluate_job(j) for j in batch]
                                        evaluated_batch.extend(await asyncio.gather(*tasks, return_exceptions=False))
                                        
                                    final_batch = [j for j in (evaluated_batch + invalid_batch) if j.get("AI Decision") != "Pending AI Review"]
                                    
                                    rows = self._format_jobs_for_db(final_batch, f"{keyword} ({location})")
                                    if rows:
                                        db_client.insert("jobs", rows)
                                        source_saved_total += len(final_batch)
                                        keyword_saved_total += len(final_batch)
                                        total_saved += len(final_batch)
                                        logger.info(f"Saved {len(final_batch)} new jobs to database from {source_name} for '{exp_kw}'.")
                                        
                                    for evaluated in final_batch:
                                        url = evaluated.get("job_url")
                                        if url:
                                            dedup.existing_urls.add(url.strip())
                                        company = evaluated.get("company", "").strip().lower()
                                        title = evaluated.get("title", "").strip().lower()
                                        if company and title:
                                            dedup.existing_signatures.add(f"{company}::{title}")

                                # Log to database for this source attempt on this expanded keyword
                                db_client.insert("logs", [{
                                    "time": datetime.now().isoformat(),
                                    "source": source_name,
                                    "keyword": f"{exp_kw} ({location})",
                                    "jobs_found": keyword_collected,
                                    "message": f"Fetched {keyword_collected} jobs, saved {source_saved_total} new from {source_name}",
                                    "status": "success" if source_saved_total > 0 else "info"
                                }])

                                # If we hit the max jobs for this original keyword across expansions, stop searching expanded keywords
                                if keyword_saved_total >= config.max_jobs_per_keyword:
                                    logger.info(f"Reached max jobs ({config.max_jobs_per_keyword}) for '{keyword}'. Skipping remaining expanded keywords.")
                                    break
                                    
                            except Exception as e:
                                logger.error(f"Error fetching from {source_name}: {e}")
                                
                            await asyncio.sleep(config.delay_between_requests)
                            
                        # Check if we got enough good jobs from this source to stop the fallback chain
                        if keyword_saved_total > 0:
                            logger.info(f"Successfully saved {keyword_saved_total} jobs from {source_name} for '{keyword}'. Skipping fallbacks.")
                            break
            
            logger.info(f"Scraping run completed in {datetime.now() - start_time}. Total collected: {total_collected}, Total saved: {total_saved}")
            
            duration = str(datetime.now() - start_time)
            
            log_row = {
                "time": datetime.now().isoformat(),
                "source": "All",
                "keyword": "All",
                "jobs_found": total_collected,
                "message": f"Fetched {total_collected} jobs, saved {total_saved} new in {duration}",
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
            logger.info("Orchestrated API fetch run completed.")

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
                "summary": j.get("summary", ""),
                "skills": j.get("skills", []),
                "category": j.get("category", "Unknown"),
                "employment_type": j.get("employment_type", ""),
                "salary": j.get("salary", ""),
                "remote": j.get("remote", False)
            })
        return rows

orchestrator = Orchestrator()

