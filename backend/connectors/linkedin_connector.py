import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright
from backend.connectors.base_connector import BaseConnector
from backend.services.session_storage import session_storage

logger = logging.getLogger(__name__)

class LinkedInConnector(BaseConnector):
    provider_id = "linkedin"

    def __init__(self):
        self.last_login: Optional[str] = None
        self.last_validation: Optional[str] = None
        self.is_connected = False
        self.is_expired = False

        # Hydrate state from storage
        if session_storage.exists(self.provider_id):
            session_data = session_storage.load(self.provider_id)
            if session_data:
                self.is_connected = True
                self.last_login = session_data.get("_meta", {}).get("last_login")
                self.last_validation = session_data.get("_meta", {}).get("last_validation")

    async def connect(self) -> Dict[str, Any]:
        """
        Launches a visible browser for the user to login to LinkedIn.
        Waits for the user to successfully login, then encrypts and saves the state.
        """
        try:
            async with async_playwright() as p:
                # Must not be headless so user can interact
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context()
                page = await context.new_page()

                await page.goto("https://www.linkedin.com/login")

                logger.info("Waiting for user to login to LinkedIn...")

                # Wait until we see the feed or a sign of successful login
                # Timeout is set high (e.g. 5 minutes) to give user time to type and pass 2FA
                try:
                    await page.wait_for_url("**/feed/**", timeout=300000)
                except Exception as e:
                    logger.warning("Timeout or error waiting for login success.")
                    await browser.close()
                    return {"status": "Error", "message": "Login timed out or failed"}

                # Login successful, grab state
                logger.info("Login successful. Saving session state.")
                state = await context.storage_state()

                # Add metadata
                now = datetime.now().isoformat()
                state["_meta"] = {
                    "last_login": now,
                    "last_validation": now
                }

                session_storage.save(self.provider_id, state)

                self.is_connected = True
                self.is_expired = False
                self.last_login = now
                self.last_validation = now

                await browser.close()
                return {"status": "Success"}

        except Exception as e:
            logger.error(f"LinkedIn connect error: {e}")
            return {"status": "Error", "message": str(e)}

    async def disconnect(self) -> bool:
        session_storage.delete(self.provider_id)
        self.is_connected = False
        self.is_expired = False
        self.last_login = None
        self.last_validation = None
        logger.info("LinkedIn disconnected.")
        return True

    async def status(self) -> Dict[str, Any]:
        status_text = "Not Connected"
        if self.is_expired:
            status_text = "Expired"
        elif self.is_connected:
            status_text = "Connected"

        return {
            "status": status_text,
            "last_login": self.last_login,
            "last_validation": self.last_validation
        }

    async def validate(self) -> bool:
        """
        Headless check to see if the session is still valid.
        """
        if not self.is_connected or not session_storage.exists(self.provider_id):
            return False

        try:
            state = session_storage.load(self.provider_id)
            if not state:
                return False

            async with async_playwright() as p:
                # remove meta before loading into playwright
                meta = state.pop("_meta", {})

                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(storage_state=state)
                page = await context.new_page()

                # Try accessing the feed
                await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")

                # Check if we got redirected to login
                if "login" in page.url or "signup" in page.url:
                    self.is_expired = True
                    logger.warning("LinkedIn session expired.")
                    await browser.close()
                    return False

                # Valid
                self.is_expired = False
                now = datetime.now().isoformat()
                self.last_validation = now

                # Update meta
                state["_meta"] = meta
                state["_meta"]["last_validation"] = now
                session_storage.save(self.provider_id, state)

                await browser.close()
                return True

        except Exception as e:
            logger.error(f"LinkedIn validation error: {e}")
            self.is_expired = True
            return False

    async def refresh(self) -> bool:
        # For LinkedIn, refresh generally requires manual re-login
        return False
