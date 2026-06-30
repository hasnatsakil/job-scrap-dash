import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class BaseConnector:
    provider_id: str = "base"

    async def connect(self) -> Dict[str, Any]:
        """Initiate connection (login flow). Returns status info."""
        raise NotImplementedError

    async def save_session(self, session_data: dict) -> bool:
        """Save an externally provided session state."""
        raise NotImplementedError

    async def disconnect(self) -> bool:
        """Clear session and disconnect."""
        raise NotImplementedError

    async def status(self) -> Dict[str, Any]:
        """Return current connection status."""
        raise NotImplementedError

    async def validate(self) -> bool:
        """Validate if the current session is still active."""
        raise NotImplementedError

    async def refresh(self) -> bool:
        """Attempt to refresh an expired session if possible."""
        raise NotImplementedError
