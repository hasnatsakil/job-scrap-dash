import pytest
from unittest.mock import patch, MagicMock
from backend.services.query_expansion import QueryExpansionService

@pytest.mark.asyncio
@patch("backend.services.query_expansion.db_client")
async def test_expand_cache_hit(mock_db_client):
    # Mock cache hit
    mock_response = MagicMock()
    mock_response.data = [{"expanded_keywords": ["Backend Dev", "API Dev"]}]
    mock_db_client.client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

    result = await QueryExpansionService.expand("Backend Dev")
    assert result == ["Backend Dev", "API Dev"]
    mock_db_client.client.table.return_value.upsert.assert_not_called()

@pytest.mark.asyncio
@patch("backend.services.query_expansion.httpx.AsyncClient")
@patch("backend.services.query_expansion.db_client")
async def test_expand_cache_miss_api_success(mock_db_client, mock_httpx_client):
    # Mock cache miss
    mock_response = MagicMock()
    mock_response.data = []
    mock_db_client.client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

    # Mock httpx response
    from unittest.mock import AsyncMock
    mock_httpx = AsyncMock()
    mock_httpx_client.return_value.__aenter__.return_value = mock_httpx
    mock_httpx_response = MagicMock()
    mock_httpx_response.json.return_value = {
        "choices": [{"message": {"content": '{"expanded_keywords": ["Python Dev", "Backend Engineer"]}'}}]
    }
    mock_httpx.post.return_value = mock_httpx_response

    result = await QueryExpansionService.expand("Python Dev")
    assert result == ["Python Dev", "Backend Engineer"]
    
    # Assert it attempts to save to cache
    mock_db_client.client.table.return_value.upsert.assert_called_once()
