import re
from typing import Dict, Any

class DataNormalizer:
    @staticmethod
    def clean_html(raw_html: str) -> str:
        if not raw_html: return ""
        raw_html = raw_html.strip()
        # If it doesn't contain standard formatting tags, it's likely plain text. Convert newlines.
        if not any(tag in raw_html.lower() for tag in ["<p", "<br", "<ul", "<li"]):
            return raw_html.replace('\n', '<br/>')
        # Otherwise, preserve the HTML!
        return raw_html

    @staticmethod
    def normalize_location(location: str) -> str:
        if not location: return "Unknown"
        loc = location.lower().strip()
        if "remote" in loc or "anywhere" in loc: return "Remote"
        return location.strip()

    @staticmethod
    def normalize_work_type(work_type: str, location: str) -> str:
        if not work_type:
            if location and "Remote" in location: return "Remote"
            return "Unknown"
        wt = work_type.lower()
        if "remote" in wt: return "Remote"
        if "hybrid" in wt: return "Hybrid"
        if "on-site" in wt or "onsite" in wt or "in-office" in wt: return "On-site"
        return work_type.strip().title()

    @staticmethod
    def normalize_employment_type(emp_type: str) -> str:
        if not emp_type: return "Full-time"
        et = emp_type.lower()
        if "full" in et and "time" in et: return "Full-time"
        if "part" in et and "time" in et: return "Part-time"
        if "contract" in et: return "Contract"
        if "intern" in et: return "Internship"
        return emp_type.strip().title()

    @classmethod
    def _extract_missing_fields_from_text(cls, job: Dict[str, Any]):
        text = job.get("description", "").lower()
        if not job.get("work_type") or job.get("work_type") == "Unknown":
            if "remote" in text:
                job["work_type"] = "Remote"
            elif "hybrid" in text:
                job["work_type"] = "Hybrid"
            elif "on-site" in text or "onsite" in text:
                job["work_type"] = "On-site"

        if not job.get("employment_type") or job.get("employment_type") == "Unknown":
            if "full-time" in text or "full time" in text:
                job["employment_type"] = "Full-time"
            elif "part-time" in text or "part time" in text:
                job["employment_type"] = "Part-time"
            elif "contract" in text:
                job["employment_type"] = "Contract"

    @classmethod
    def normalize_job(cls, job: Dict[str, Any]) -> Dict[str, Any]:
        # HTML cleaning is now handled by the API providers, but we can do a fallback
        if "raw_html" in job:
            del job["raw_html"]
            
        cls._extract_missing_fields_from_text(job)
        
        loc = cls.normalize_location(job.get("location", ""))
        job["location"] = loc
        job["work_type"] = cls.normalize_work_type(job.get("work_type", ""), loc)
        job["employment_type"] = cls.normalize_employment_type(job.get("employment_type", ""))
        return job
