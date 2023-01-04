"""Модуль ожидающий принятия соединения от Redis."""
import sys
import time

from redis import asyncio as redisio
from redis.exceptions import ConnectionError
import asyncio
print(f"{sys.path[0]}\..")
sys.path.append(f"{sys.path[0]}/..")

from settings import test_settings

async def check():
    url = test_settings.redis_conn_str
    async with redisio.from_url( url, db=0 ) as connection:
        while True:
            try:
                await connection.ping()
                break
            except ConnectionError:
                time.sleep(1)
            except Exception as e:
                raise e



if __name__ == '__main__':
    asyncio.run(check())