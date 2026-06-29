from typing import Dict, Any
from backend.config import config_manager

class KeywordFilter:
    @staticmethod
    def is_relevant(job: Dict[str, Any]) -> bool:
        config = config_manager.get_config()
        keywords = config.search_keywords
        if not keywords: return True
        text_to_search = f"{job.get('title', '')} {job.get('description', '')}".lower()
        for keyword in keywords:
            if keyword.lower() in text_to_search:
                return True
        return False
