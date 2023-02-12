"""Модуль фикстур"""
import asyncio

import pytest


pytest_plugins = [
    "functional.fixtures.api",
    "functional.fixtures.es",
    "functional.fixtures.redis"
]


@pytest.fixture(scope="session")
def event_loop():
    """Создадим экземпляр цикла событий по умолчанию, для всей сессии."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()




