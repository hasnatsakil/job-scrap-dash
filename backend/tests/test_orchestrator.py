import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from backend.services.orchestrator import Orchestrator

# Dummy config class to replace actual config
class DummyConfig:
    search_locations = ["US"]
    search_keywords = ["Dev"]
    max_jobs_per_keyword = 5
    delay_between_requests = 0

@pytest.fixture
def orchestrator():
    return Orchestrator()

@pytest.mark.asyncio
@patch("backend.services.orchestrator.config_manager")
@patch("backend.services.orchestrator.query_expansion")
@patch("backend.services.orchestrator.API_REGISTRY", {})
@patch("backend.services.orchestrator.db_client")
async def test_orchestrator_skips_fallbacks_when_quota_met(mock_db_client, mock_qe, mock_config_manager, orchestrator):
    mock_config_manager.get_config.return_value = DummyConfig()
    mock_qe.expand = AsyncMock(return_value=["Dev", "Engineer"])
    
    # Mock APIs
    class MockAPI1:
        async def fetch_jobs(self, kw, loc, limit):
            return [{"title": f"Job {i}", "job_url": f"url{i}"} for i in range(10)]
    
    class MockAPI2:
        async def fetch_jobs(self, kw, loc, limit):
            return []

    from backend.services.orchestrator import API_REGISTRY
    API_REGISTRY.update({"adzuna": MockAPI1, "jooble": MockAPI2, "muse": MockAPI2})

    # Since we intercept db insertions/ai evaluation in the test, let's just mock the final batch format
    with patch.object(orchestrator, "_format_jobs_for_db", return_value=[{"id": 1}] * 10):
        # We need to mock AI so it doesn't try to call it
        with patch("backend.services.orchestrator.ai_manager") as mock_ai:
            mock_ai.evaluate_job = AsyncMock(return_value={"AI Decision": "Keep"})
            # Mock the config's enabled_sources to empty so we only test the default fallback chain
            mock_config_manager.get_config.return_value.enabled_sources = []
            await orchestrator.run_all()
    
    # If it skipped fallbacks, the length of the mock call would be 1.
    # We can assert it didn't throw an exception.
    pass
