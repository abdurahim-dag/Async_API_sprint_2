import aiohttp
import pytest_asyncio


@pytest_asyncio.fixture(scope='session')
async def client_session(redis_client, request):
    """Создадим экземпляр сессии aiohttp, для всей сессии."""
    async with aiohttp.ClientSession() as session:
        yield session


@pytest_asyncio.fixture
async def make_get_request(client_session):
    """Собственно запрос к API посредством aiohttp сессии."""
    async def go(url, params=None):
        async with client_session.get(url=url, params=params, allow_redirects=True) as response:
            print(url)
            response.json = await response.json()
            return response
    return go
