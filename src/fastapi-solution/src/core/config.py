import os
from logging import config as logging_config

from pydantic import BaseSettings

from core.logger import LOGGING


class Environments(BaseSettings):
    PROJECT_NAME: str
    REDIS_HOST: str
    REDIS_PORT: int
    ELASTIC_HOST: str
    ELASTIC_PORT: int
    BASE_DIR: str
    ORIGINS: list[str]


# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

config: Environments | None = None


def config_build():
    return Environments(
        PROJECT_NAME=os.getenv('PROJECT_NAME', 'movies'),
        REDIS_HOST=os.getenv('REDIS_HOST'),
        REDIS_PORT=int(os.getenv('REDIS_PORT')),
        ELASTIC_HOST=os.getenv('ES_HOST'),
        ELASTIC_PORT=int(os.getenv('ES_PORT')),
        BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        ORIGINS=[
            'http://localhost:80',
        ]
    )


if not config:
    config = config_build()
