import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from asyncpg.exceptions import InvalidCatalogNameError
from infra_ai_service.core.app import get_app
from fastapi import FastAPI
from httpx import AsyncClient


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:  # : indirect usage
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncGenerator:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
def app() -> FastAPI:
    return get_app()

