"""Main Tests"""
import json

from context import *  # noqa
from context import pytest, AsyncClient

class TestMain:
    @pytest.mark.anyio
    @pytest.mark.dependency()
    async def test_root(self, client: AsyncClient):
        response = await client.get("/")
        data = response.json()
        assert response.status_code == 200
        assert type(data) is dict
        for key in ['body', 'footer', 'tax', 'hourly_rate', 'company', 'customer', 'positions']:
            assert key in data

    @pytest.mark.anyio
    @pytest.mark.dependency(depends='TestMain::test_root')
    async def test_create_pdf(self, client: AsyncClient):
        with open('example.json', 'r') as f:
            data = json.load(f)

        response = await client.post("/", json=data)
        assert response.text[1:4] == 'PDF'
        assert response.status_code == 200
