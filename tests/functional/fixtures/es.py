"""Модуль фикстур"""
import linecache
import random
from contextlib import closing
from typing import Generator

import elasticsearch
import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch

from functional.settings import ESIndexSettings, settings
from .utils import check


@pytest_asyncio.fixture(scope='session')
async def es_client() -> Generator[AsyncElasticsearch, None, None]:
    """Создадим экземпляр асинхронного клиента ES, для всей сессии."""
    async with AsyncElasticsearch(hosts=[settings.es_conn_str]) as client:
        await check(client)
        yield client


@pytest_asyncio.fixture(scope='session')
async def es_init(es_client: AsyncElasticsearch, request):
    """Инициализация индекса."""
    settings: ESIndexSettings = request.param
    index_name = settings.index_name
    with closing(open(settings.schema_file_path, 'rt', encoding='utf-8')) as findex:
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
        with closing(open(settings.data_file_path, 'rt', encoding='utf-8')) as fdata:
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
            await es_client.indices.delete(index=index_name)


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
