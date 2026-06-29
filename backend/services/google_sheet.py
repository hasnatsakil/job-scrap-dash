import base64
import json
import logging
from typing import List, Dict, Any, Optional
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from backend.config import env_settings

logger = logging.getLogger(__name__)
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class GoogleSheetsService:
    def __init__(self):
        self.spreadsheet_id = env_settings.google_sheet_id
        self.credentials = self._load_credentials()
        self.service = build('sheets', 'v4', credentials=self.credentials) if self.credentials else None

    def _load_credentials(self) -> Optional[Credentials]:
        if not env_settings.google_sheets_credentials_b64:
            logger.error("GOOGLE_SHEETS_CREDENTIALS_B64 is not set")
            return None
        try:
            creds_json = base64.b64decode(env_settings.google_sheets_credentials_b64).decode('utf-8')
            return Credentials.from_service_account_info(json.loads(creds_json), scopes=SCOPES)
        except Exception as e:
            logger.error(f"Failed to load Google Sheets credentials: {e}")
            return None

    def initialize_sheets(self):
        if not self.service: return
        required_tabs = {
            'Jobs': ['Scraped Date', 'Job Title', 'Company', 'Location', 'Work Type', 'Employment Type', 'Salary', 'Experience', 'Source', 'Job URL', 'Posted Date', 'AI Score', 'AI Decision', 'AI Reason'],
            'Settings': ['Key', 'Value'],
            'Logs': ['Time', 'Source', 'Keyword', 'Jobs Found', 'Jobs Saved', 'Errors', 'Duration', 'Status'],
            'Keywords': ['Keyword', 'Location', 'Enabled'],
            'Sources': ['Source', 'Enabled'],
            'Sessions': ['Provider', 'EncryptedState']
        }
        try:
            sheet_metadata = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
            existing_tabs = {sheet['properties']['title']: sheet['properties']['sheetId'] for sheet in sheet_metadata.get('sheets', [])}
            requests = [{"addSheet": {"properties": {"title": t}}} for t in required_tabs.keys() if t not in existing_tabs]
            if requests:
                self.service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id, body={'requests': requests}).execute()
                for t, headers in required_tabs.items():
                    if t not in existing_tabs:
                         self.service.spreadsheets().values().update(spreadsheetId=self.spreadsheet_id, range=f"{t}!A1", valueInputOption="RAW", body={"values": [headers]}).execute()
        except HttpError as err: logger.error(f"Google Sheets API error: {err}")

    def get_all_rows(self, sheet_name: str) -> List[Dict[str, Any]]:
        if not self.service: return []
        try:
            result = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=sheet_name).execute()
            values = result.get('values', [])
            if not values or len(values) < 2: return []
            headers = values[0]
            return [{headers[i]: row[i] if i < len(row) else "" for i in range(len(headers))} for row in values[1:]]
        except HttpError: return []

    def append_rows(self, sheet_name: str, rows: List[List[Any]]):
        if not self.service or not rows: return
        try: self.service.spreadsheets().values().append(spreadsheetId=self.spreadsheet_id, range=f"{sheet_name}!A:A", valueInputOption="USER_ENTERED", insertDataOption="INSERT_ROWS", body={'values': rows}).execute()
        except HttpError: pass

    def clear_and_update(self, sheet_name: str, headers: List[str], rows: List[List[Any]]):
        if not self.service: return
        try:
            self.service.spreadsheets().values().clear(spreadsheetId=self.spreadsheet_id, range=sheet_name, body={}).execute()
            self.service.spreadsheets().values().update(spreadsheetId=self.spreadsheet_id, range=f"{sheet_name}!A1", valueInputOption="USER_ENTERED", body={'values': [headers] + rows}).execute()
        except HttpError: pass

google_sheets_service = GoogleSheetsService()
