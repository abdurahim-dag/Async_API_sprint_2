"""Модуль фикстур"""
import logging

import elasticsearch
import pytest_asyncio
import pytest
import aiohttp
from redis import asyncio as redisio
import asyncio
import random
import linecache
from contextlib import closing
from elasticsearch import AsyncElasticsearch
from .settings import ESIndexSettings, settings, indexes
from typing import Generator

@pytest.fixture(scope="session")
def event_loop():
    """Создадим экземпляр цикла событий по умолчанию, для всей сессии."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope='session')
async def es_client() -> Generator[AsyncElasticsearch, None, None]:
    """Создадим экземпляр асинхронного клиента ES, для всей сессии."""
    client = AsyncElasticsearch(hosts=[settings.es_conn_str])
    yield client
    await client.close()

@pytest_asyncio.fixture(scope='session')
async def es_init(es_client: AsyncElasticsearch):
    """Инициализация индекса."""
    for index in indexes:
        index_name = index.index_name
        with closing(open(index.schema_file_path, 'rt', encoding='utf-8')) as findex:
            body = findex.read()
            try:
                await es_client.indices.delete([index_name])
            except elasticsearch.exceptions.NotFoundError as e:
                pass
            # Создадим индекс.
            await es_client.indices.create(
                index=index_name,
                body=body,
            )
            with closing(open(index.data_file_path, 'rt', encoding='utf-8')) as fdata:
                # Наполним индекс данными из файла.
                body = fdata.read()
                await es_client.bulk(
                    index=index_name,
                    body=body,
                )
                await es_client.indices.refresh(index=index_name)

    # Продолжим наши тесты.
    yield

    # Грохнем индекс.
    for index in indexes:
        index_name = index.index_name
        await es_client.indices.delete(index=index_name)


@pytest_asyncio.fixture(scope='session')
async def redis_client():
    """Создадим экземпляр асинхронного клиента Redis, для всей сессии."""
    async with redisio.from_url(settings.redis_conn_str,db=settings.redis_db) as client:
        yield client

@pytest.fixture(scope='session')
def random_line(request):
    """Выберем рандомную строку с данными для модели, для теста."""
    fpath=request.param
    # В соответствии с правилами bulk загрузки данных в индекс,
    # конкретный документ лежит через строку после строки с описанием параметрами целевого индекса.
    # И последняя строка пустая, что нам не интересно.
    num_lines = len(open(fpath, 'rt', encoding='utf-8').readlines()) - 1
    num_line = random.randrange(2,num_lines,2)
    return linecache.getline(str(fpath), num_line)


@pytest_asyncio.fixture(scope='session')
async def client_session(request):
    """Создадим экземпляр сессии aiohttp, для всей сессии."""
    async with aiohttp.ClientSession() as session:
        yield session


@pytest_asyncio.fixture
async def make_get_request(client_session):
    """Собственно запрос к API посредством aiohttp сессии."""
    async def go(url, params=None):
        async with client_session.get(url=url, params=params, allow_redirects=True) as response:
            response.json = await response.json()
            return response
    return go
