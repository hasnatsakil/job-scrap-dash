import logging
from typing import Dict, Any, List, Optional
from backend.connectors.base_connector import BaseConnector

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self._connectors: Dict[str, BaseConnector] = {}

    def register_connector(self, connector: BaseConnector):
        self._connectors[connector.provider_id] = connector
        logger.info(f"Registered connector: {connector.provider_id}")

    def get_connector(self, provider_id: str) -> Optional[BaseConnector]:
        return self._connectors.get(provider_id)

    async def get_all_statuses(self) -> Dict[str, Any]:
        statuses = {}
        for provider_id, connector in self._connectors.items():
            try:
                statuses[provider_id] = await connector.status()
            except Exception as e:
                logger.error(f"Error getting status for {provider_id}: {e}")
                statuses[provider_id] = {"status": "Error", "message": str(e)}
        return statuses

    async def validate_all(self):
        """Run validation on all registered connectors."""
        for provider_id, connector in self._connectors.items():
            try:
                await connector.validate()
            except Exception as e:
                logger.error(f"Validation failed for {provider_id}: {e}")

connection_manager = ConnectionManager()
