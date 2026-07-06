import logging
from typing import Dict, Any, List
from backend.config import config_manager

logger = logging.getLogger(__name__)

class ContentValidator:
    def validate(self, job: Dict[str, Any]) -> bool:
        """
        Lightweight validation step after cleaning and before AI evaluation.
        Ensures the job has the absolute minimum required fields to be evaluated by AI.
        """
        required_fields = ["title", "company"]
        for field in required_fields:
            val = job.get(field)
            if not val or str(val).strip() == "" or str(val).lower() == "unknown":
                logger.warning(f"Validation failed: missing required field '{field}' for job {job.get('job_url')}")
                return False
                
        # Optional: ensure we aren't passing raw_html to AI by mistake
        if "raw_html" in job:
            logger.warning(f"Validation failed: raw_html still present in job {job.get('title')}")
            return False
            
        return True

    def _mark_rejected(self, job: Dict[str, Any], reason: str):
        job["AI Decision"] = "Reject"
        job["AI Reason"] = reason
        job["AI Score"] = 0

    def _is_ai_focused_keyword(self, keyword: str, trigger_terms: List[str]) -> bool:
        kw = (keyword or "").lower()
        return any(term in kw for term in trigger_terms)

    def _passes_relevance_gate(self, job: Dict[str, Any], keyword: str) -> (bool, str):
        config = config_manager.get_config()
        if not config.relevance_strict_mode or not self._is_ai_focused_keyword(keyword, config.relevance_ai_trigger_terms):
            return True, ""

        title = str(job.get("title", "")).lower()
        description = str(job.get("description", "")).lower()
        combined = f"{title} {description}"

        has_required_signal = any(term in combined for term in config.relevance_required_terms)
        has_title_required_signal = any(term in title for term in config.relevance_required_terms)
        has_blocked_generic_title = any(term in title for term in config.relevance_blocked_title_terms)

        if not has_required_signal:
            return False, f"Rejected by relevance gate for keyword '{keyword}': missing AI/ML role signals in title/description."

        if has_blocked_generic_title and not has_title_required_signal:
            return False, f"Rejected by relevance gate for keyword '{keyword}': generic software title without explicit AI specialization."

        return True, ""

    def validate_batch(self, jobs: List[Dict[str, Any]], keyword: str = "") -> List[Dict[str, Any]]:
        valid_jobs = []
        for job in jobs:
            if self.validate(job):
                passes_relevance, reason = self._passes_relevance_gate(job, keyword)
                if not passes_relevance:
                    self._mark_rejected(job, reason)
                valid_jobs.append(job)
            else:
                # Mark as rejected by validation so we don't drop it entirely, but we skip AI evaluation
                self._mark_rejected(job, "Failed lightweight validation step (missing critical fields)")
                valid_jobs.append(job) # Keep it in the pipeline, but marked as rejected
        return valid_jobs

content_validator = ContentValidator()
