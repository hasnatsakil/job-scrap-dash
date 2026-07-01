import logging
import json
import httpx
from typing import List
from backend.config import env_settings, config_manager
from backend.services.database import db_client

logger = logging.getLogger(__name__)

class QueryExpansionService:
    @classmethod
    async def expand(cls, keyword: str) -> List[str]:
        keyword = keyword.strip()
        normalized_query = keyword.lower()
        
        # 1. Check Cache
        if db_client.client:
            try:
                response = db_client.client.table("search_query_expansions")\
                                    .select("expanded_keywords")\
                                    .eq("query", normalized_query)\
                                    .execute()
                if response.data:
                    logger.info(f"Query expansion cache hit for '{keyword}'")
                    return response.data[0].get("expanded_keywords", [keyword])
            except Exception as e:
                # If table doesn't exist yet, we will just proceed
                logger.warning(f"Cache check failed (table might be missing): {e}")

        logger.info(f"Query expansion cache miss for '{keyword}'. Calling AI...")
        
        # 2. Call AI
        expanded = [keyword]
        config = config_manager.get_config()
        model = config.ai_model
        
        if ":free" not in model.lower():
            model = "openai/gpt-oss-20b:free"
            
        system_content = (
            "You are an AI Query Expansion Service for a job search application.\n"
            "Your objective is to maximize relevant job coverage while maintaining search quality.\n"
            "Generate between 5 and 10 closely related job titles and synonyms for the given search query.\n"
            "RULES:\n"
            "- Return ONLY valid JSON containing a list of strings.\n"
            "- Return titles that are commonly used in hiring.\n"
            "- Include the original search query.\n"
            "- DO NOT change the profession.\n"
            "- DO NOT add unrelated careers, skills, or programming languages.\n"
            "- DO NOT add explanations or markdown (other than JSON).\n"
            "FORMAT:\n"
            "{\n"
            "  \"expanded_keywords\": [\"Title 1\", \"Title 2\"]\n"
            "}"
        )
        user_content = f"Search query: {keyword}"
        
        headers = {
            "Authorization": f"Bearer {env_settings.openrouter_api_key}", 
            "HTTP-Referer": "https://github.com/ai-job-scraper", 
            "X-Title": "AI Job Scraper", 
            "Content-Type": "application/json"
        }
        payload = {
            "model": model, 
            "response_format": {"type": "json_object"}, 
            "messages": [
                {"role": "system", "content": system_content}, 
                {"role": "user", "content": user_content}
            ]
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"]
                
                result = json.loads(content)
                expanded = result.get("expanded_keywords", [keyword])
                
                # ensure original keyword is always included and clean up
                expanded = [str(x).strip() for x in expanded if str(x).strip()]
                if not any(k.lower() == keyword.lower() for k in expanded):
                    expanded.insert(0, keyword)
                    
                # trim to 10
                expanded = expanded[:10]
        except Exception as e:
            logger.error(f"Error generating query expansion for '{keyword}': {e}")
            return [keyword]

        # 3. Save to Cache
        if db_client.client:
            try:
                db_client.client.table("search_query_expansions").upsert({
                    "query": normalized_query,
                    "expanded_keywords": expanded
                }).execute()
            except Exception as e:
                logger.error(f"Error saving query expansion to cache: {e}")

        return expanded

query_expansion = QueryExpansionService()
