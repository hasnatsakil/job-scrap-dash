import logging
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from backend.config import env_settings

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        self.url = env_settings.supabase_url
        self.key = env_settings.supabase_key
        self.client: Optional[Client] = None
        self._initialize_client()

    def _initialize_client(self):
        if not self.url or not self.key:
            logger.error("SUPABASE_URL or SUPABASE_KEY is missing. Database connection will fail.")
            return
        
        try:
            self.client = create_client(self.url, self.key)
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self.client = None

    def verify_connection(self) -> bool:
        if not self.client:
            logger.error("Database client is not initialized.")
            return False
        try:
            # A simple query to verify connection (e.g., getting 1 row from jobs table)
            self.client.table("jobs").select("*").limit(1).execute()
            logger.info("Successfully connected to Supabase database.")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Supabase database: {e}")
            return False

    def get_all(self, table: str) -> List[Dict[str, Any]]:
        if not self.client:
            return []
        try:
            # Note: supabase-py limit defaults to 1000 if not specified, 
            # for a true "get all", pagination might be needed for large tables,
            # but we'll use a large limit for now to emulate the previous sheet behavior.
            response = self.client.table(table).select("*").limit(10000).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching from table {table}: {e}")
            return []

    def insert(self, table: str, rows: List[Dict[str, Any]]):
        if not self.client or not rows:
            return
        try:
            self.client.table(table).insert(rows).execute()
        except Exception as e:
            logger.error(f"Error inserting into table {table}: {e}")

    def clear_and_insert(self, table: str, rows: List[Dict[str, Any]]):
        """Used to replace data (e.g., for settings or keywords if we want to overwrite)."""
        if not self.client:
            return
        try:
            # Supabase doesn't have a simple 'truncate' without raw SQL in the REST API,
            # but we can delete all if there's a reliable primary key, or use upsert.
            # For simplicity, if we don't have PKs, we might just insert and accept duplicates
            # or require the caller to handle deletion first.
            # Assuming we can delete by a dummy condition or we just do upsert.
            # We'll log a warning since dropping all rows via REST API requires a filter.
            logger.warning(f"clear_and_insert called on {table}. Doing insert instead. Consider Upsert if PK exists.")
            if rows:
                self.client.table(table).insert(rows).execute()
        except Exception as e:
            logger.error(f"Error in clear_and_insert for table {table}: {e}")

    def get_keywords(self) -> List[Dict[str, Any]]:
        if not self.client:
            return []
        try:
            response = self.client.table("keywords").select("*").order("created_at").execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching keywords: {e}")
            return []

    def add_keyword(self, keyword: str, enabled: bool = True) -> Optional[Dict[str, Any]]:
        if not self.client:
            return None
        try:
            response = self.client.table("keywords").insert({
                "keyword": keyword,
                "enabled": enabled
            }).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error adding keyword '{keyword}': {e}")
            return None

    def update_keyword(self, keyword_id: str, data: Dict[str, Any]) -> bool:
        if not self.client:
            return False
        try:
            self.client.table("keywords").update(data).eq("id", keyword_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error updating keyword {keyword_id}: {e}")
            return False

    def delete_keyword(self, keyword_id: str) -> bool:
        if not self.client:
            return False
        try:
            self.client.table("keywords").delete().eq("id", keyword_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting keyword {keyword_id}: {e}")
            return False

    def update_jobs_keyword(self, old_keyword: str, new_keyword: str) -> bool:
        if not self.client:
            return False
        try:
            self.client.table("jobs").update({"keyword": new_keyword}).eq("keyword", old_keyword).execute()
            return True
        except Exception as e:
            logger.error(f"Error updating jobs keyword from '{old_keyword}' to '{new_keyword}': {e}")
            return False

    def replace_all_keywords(self, keywords: List[Dict[str, Any]]) -> bool:
        if not self.client:
            return False
        try:
            self.client.table("keywords").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            if keywords:
                self.client.table("keywords").insert(keywords).execute()
            return True
        except Exception as e:
            logger.error(f"Error replacing keywords: {e}")
            return False

    # ── Sources ──────────────────────────────────────────────────────────────

    def get_sources(self) -> List[Dict[str, Any]]:
        """Fetch all source rows from the sources table."""
        if not self.client:
            return []
        try:
            response = self.client.table("sources").select("*").execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching sources: {e}")
            return []

    def upsert_source(self, name: str, enabled: bool) -> bool:
        """Insert or update a source row by name."""
        if not self.client:
            return False
        try:
            self.client.table("sources").upsert(
                {"name": name, "enabled": enabled},
                on_conflict="name"
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Error upserting source '{name}': {e}")
            return False

    def upsert_all_sources(self, sources: List[Dict[str, Any]]) -> bool:
        """Bulk upsert all source rows."""
        if not self.client or not sources:
            return False
        try:
            self.client.table("sources").upsert(sources, on_conflict="name").execute()
            return True
        except Exception as e:
            logger.error(f"Error upserting sources: {e}")
            return False

db_client = DatabaseService()
