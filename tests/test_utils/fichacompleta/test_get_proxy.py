import pytest
from unittest.mock import AsyncMock, patch
from utils.fichacompleta.get_proxy import get_proxy

@pytest.mark.asyncio
@patch('utils.fichacompleta.get_proxy.PROXIES', ['http://mockproxy.com'])
@patch('utils.fichacompleta.get_proxy.httpx.AsyncClient')
async def test_get_proxy_sucess(MockClient):
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>OK</body></html>"

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    MockClient.return_value.__aenter__.return_value = mock_client

    response = await get_proxy("http://test.com", headers={})
    assert "OK" in response