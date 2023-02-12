import pytest_asyncio
from redis import asyncio as redisio

from functional.settings import settings
from .utils import check


@pytest_asyncio.fixture(scope='session')
async def redis_client():
    """Создадим экземпляр асинхронного клиента Redis, для всей сессии."""
    async with redisio.from_url(settings.redis_conn_str,db=settings.redis_db) as client:
        await check(client)
        yield client
