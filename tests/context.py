import pytest
from httpx import ASGITransport, AsyncClient
import logging

from src.main import app

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(name="client", scope="session")
async def client_fixture():
    async with ASGITransport(app=app) as transport:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
