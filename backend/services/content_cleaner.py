import logging
import re
from typing import Dict, Any

logger = logging.getLogger(__name__)

BOILERPLATE_PATTERNS = [
    r'(?i)equal opportunity employer.*?(?:\.\n|$)',
    r'(?i)we are an equal opportunity employer.*?(?:\.\n|$)',
    r'(?i)eeo[^.]*\.',
    r'(?i)reasonable accommodation.*?(?:\.\n|$)',
    r'(?i)qualified applicants.*?(?:\.\n|$)',
    r'(?i)apply (?:now|today|here).*?(?:\.\n|$)',
    r'(?i)share this.*?(?:\n|$)',
    r'(?i)save this.*?(?:\n|$)',
    r'(?i)similar jobs.*?(?:\n|$)',
    r'(?i)recommended jobs.*?(?:\n|$)',
    r'(?i)privacy policy.*?(?:\.\n|$)',
    r'(?i)cookie.*?(?:\.\n|$)',
    r'(?i)by submitting.*?(?:\.\n|$)',
    r'(?i)we will contact.*?(?:\.\n|$)',
    r'(?i)unsolicited.*?(?:\.\n|$)',
    r'(?i)agency.*?(?:\.\n|$)',
    r'(?i)recruiter.*?(?:\.\n|$)',
]

class ContentCleaner:
    def clean(self, job: Dict[str, Any]) -> Dict[str, Any]:
        if "raw_html" in job:
            del job["raw_html"]

        desc = job.get("description", "")
        if desc:
            for pattern in BOILERPLATE_PATTERNS:
                desc = re.sub(pattern, '', desc)
            desc = re.sub(r'\n\s*\n', '\n\n', desc).strip()
            job["description"] = desc

        return job

content_cleaner = ContentCleaner()
