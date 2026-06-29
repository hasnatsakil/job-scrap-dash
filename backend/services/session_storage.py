import json
import logging
from typing import Optional
from cryptography.fernet import Fernet
import base64
from backend.config import env_settings
from backend.services.google_sheet import google_sheets_service

logger = logging.getLogger(__name__)

class SessionStorageInterface:
    def save(self, provider_id: str, data: dict) -> bool: raise NotImplementedError
    def load(self, provider_id: str) -> Optional[dict]: raise NotImplementedError
    def delete(self, provider_id: str) -> bool: raise NotImplementedError
    def exists(self, provider_id: str) -> bool: raise NotImplementedError

class GoogleSheetsSessionStorage(SessionStorageInterface):
    """
    Stores encrypted session state directly in Google Sheets 'Sessions' tab
    to survive ephemeral Vercel serverless function restarts.
    """
    def __init__(self):
        raw_key = env_settings.session_encryption_key.encode('utf-8')
        if len(raw_key) < 32: raw_key = raw_key.ljust(32, b'x')
        elif len(raw_key) > 32: raw_key = raw_key[:32]
        self.fernet = Fernet(base64.urlsafe_b64encode(raw_key))
        self.sheet_name = "Sessions"

    def save(self, provider_id: str, data: dict) -> bool:
        try:
            encrypted_data = self.fernet.encrypt(json.dumps(data).encode('utf-8')).decode('utf-8')
            rows = google_sheets_service.get_all_rows(self.sheet_name)

            # Update if exists, else append
            updated = False
            new_rows = []
            for r in rows:
                if r.get("Provider") == provider_id:
                    r["EncryptedState"] = encrypted_data
                    updated = True
                new_rows.append([r.get("Provider", ""), r.get("EncryptedState", "")])

            if not updated:
                new_rows.append([provider_id, encrypted_data])

            google_sheets_service.clear_and_update(self.sheet_name, ["Provider", "EncryptedState"], new_rows)
            return True
        except Exception as e:
            logger.error(f"Failed to save session to Sheets: {e}")
            return False

    def load(self, provider_id: str) -> Optional[dict]:
        try:
            rows = google_sheets_service.get_all_rows(self.sheet_name)
            for r in rows:
                if r.get("Provider") == provider_id:
                    enc_data = r.get("EncryptedState", "")
                    if enc_data:
                        decrypted = self.fernet.decrypt(enc_data.encode('utf-8')).decode('utf-8')
                        return json.loads(decrypted)
            return None
        except Exception as e:
            logger.error(f"Failed to load session from Sheets: {e}")
            return None

    def delete(self, provider_id: str) -> bool:
        try:
            rows = google_sheets_service.get_all_rows(self.sheet_name)
            new_rows = [[r.get("Provider"), r.get("EncryptedState")] for r in rows if r.get("Provider") != provider_id]
            google_sheets_service.clear_and_update(self.sheet_name, ["Provider", "EncryptedState"], new_rows)
            return True
        except Exception as e:
            logger.error(f"Failed to delete session from Sheets: {e}")
            return False

    def exists(self, provider_id: str) -> bool:
        rows = google_sheets_service.get_all_rows(self.sheet_name)
        return any(r.get("Provider") == provider_id for r in rows)

# Use Sheets storage for Vercel
session_storage = GoogleSheetsSessionStorage()
