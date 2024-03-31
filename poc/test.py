from unittest import mock

import pytest
from httpx import AsyncClient

from app import app, Service, container
import pytest_asyncio

@pytest_asyncio.fixture
#@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_index(client):
    service_mock = mock.AsyncMock(spec=Service)
    service_mock.process.return_value = "Foo"

    with container.service.override(service_mock):
        response = await client.get("/")

    assert response.status_code == 200
    assert response.json() == {"result": "Foo"}