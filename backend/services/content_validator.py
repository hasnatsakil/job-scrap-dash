import logging
from typing import Dict, Any, List

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

    def validate_batch(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        valid_jobs = []
        for job in jobs:
            if self.validate(job):
                valid_jobs.append(job)
            else:
                # Mark as rejected by validation so we don't drop it entirely, but we skip AI evaluation
                job["AI Decision"] = "Reject"
                job["AI Reason"] = "Failed lightweight validation step (missing critical fields)"
                job["AI Score"] = 0
                valid_jobs.append(job) # Keep it in the pipeline, but marked as rejected
        return valid_jobs

content_validator = ContentValidator()
