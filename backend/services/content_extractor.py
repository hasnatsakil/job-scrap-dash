import logging
import re
from typing import Dict, Any
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class ContentExtractor:
    SOURCE_SELECTORS = {
        "linkedin": [
            "div.description__text div",
            ".show-more-less-html__markup",
            "article",
        ],
        "lever": [
            ".posting-description",
            ".content",
            ".page-content",
            "main",
        ],
        "greenhouse": [
            "#description",
            ".job-description",
            ".content",
            "main",
        ],
        "ashby": [
            "[data-testid='JobDescriptionContainer']",
            ".job-description",
            ".content",
            "main",
        ],
    }

    def extract(self, job: Dict[str, Any]) -> Dict[str, Any]:
        raw_html = job.get("raw_html")
        if not raw_html:
            return job

        source = job.get("source", "").lower()
        soup = BeautifulSoup(raw_html, "html.parser")

        # Extract structured criteria from LinkedIn job pages before text-based fallback
        if source == "linkedin":
            self._extract_linkedin_criteria(soup, job)
        
        # Try source-specific selectors first, fall back to generic
        text = self._extract_source_specific(soup, source)
        if not text or len(text.strip()) < 50:
            text = self._extract_generic(soup)

        cleaned_text = re.sub(r'\n\s*\n', '\n\n', text)
        cleaned_text = re.sub(r' +', ' ', cleaned_text).strip()

        if cleaned_text:
            job["description"] = cleaned_text

        # Extract basic fields if they are missing (text-based fallback)
        self._extract_fields(job, cleaned_text)

        return job

    def _extract_source_specific(self, soup: BeautifulSoup, source: str) -> str:
        selectors = self.SOURCE_SELECTORS.get(source, [])
        for selector in selectors:
            container = soup.select_one(selector)
            if container:
                self._remove_junk(container)
                return container.get_text(separator="\n")
        return ""

    def _remove_junk(self, element):
        for tag in element.find_all(["script", "style", "nav", "footer", "header", "aside", "form", "noscript", "iframe"]):
            tag.decompose()

    def _extract_generic(self, soup: BeautifulSoup) -> str:
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "form", "button", "noscript", "iframe", "svg"]):
            element.decompose()
        return soup.get_text(separator="\n")

    def _extract_linkedin_criteria(self, soup: BeautifulSoup, job: Dict[str, Any]):
        criteria_items = soup.select(".job-criteria__item")
        for item in criteria_items:
            subtitle_elem = item.select_one(".job-criteria__subtitle")
            text_elem = item.select_one(".job-criteria__text")
            if not subtitle_elem or not text_elem:
                continue
            subtitle = subtitle_elem.get_text(strip=True).lower()
            value = text_elem.get_text(strip=True)
            if not value:
                continue

            if "seniority" in subtitle or "experience level" in subtitle:
                if not job.get("experience"):
                    job["experience"] = value

            if "employment type" in subtitle:
                if not job.get("employment_type"):
                    vl = value.lower()
                    if "full" in vl and "time" in vl:
                        job["employment_type"] = "Full-time"
                    elif "part" in vl and "time" in vl:
                        job["employment_type"] = "Part-time"
                    elif "contract" in vl:
                        job["employment_type"] = "Contract"
                    elif "intern" in vl:
                        job["employment_type"] = "Internship"
                    else:
                        job["employment_type"] = value

            if any(w in subtitle for w in ["remote", "work type", "on-site", "onsite"]):
                if not job.get("work_type"):
                    vl = value.lower()
                    if "remote" in vl:
                        job["work_type"] = "Remote"
                    elif "hybrid" in vl:
                        job["work_type"] = "Hybrid"
                    elif "on-site" in vl or "onsite" in vl or "in-office" in vl:
                        job["work_type"] = "On-site"
                    else:
                        job["work_type"] = value

    def _extract_fields(self, job: Dict[str, Any], text: str):
        lower_text = text.lower()
        if not job.get("work_type"):
            if "remote" in lower_text:
                job["work_type"] = "Remote"
            elif "hybrid" in lower_text:
                job["work_type"] = "Hybrid"
            elif "on-site" in lower_text or "onsite" in lower_text:
                job["work_type"] = "On-site"

        if not job.get("employment_type"):
            if "full-time" in lower_text or "full time" in lower_text:
                job["employment_type"] = "Full-time"
            elif "part-time" in lower_text or "part time" in lower_text:
                job["employment_type"] = "Part-time"
            elif "contract" in lower_text:
                job["employment_type"] = "Contract"

content_extractor = ContentExtractor()
