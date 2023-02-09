"""Модуль ожидающий принятия соединения от ES."""
import sys
import time
import asyncio
from logger import logger
from elasticsearch import AsyncElasticsearch

sys.path.append(f"{sys.path[0]}/..")
from settings import settings


async def check():
    es_client = AsyncElasticsearch(hosts=settings.es_conn_str, validate_cert=False, use_ssl=False)
    while True:
        if await es_client.ping():
            break
        logger.error("Expectation ES online %s", settings.es_conn_str)
        time.sleep(1)
    await es_client.close()

if __name__ == '__main__':
    asyncio.run(check())
