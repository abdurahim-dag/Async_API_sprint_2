import os
from logging import config as logging_config

from pydantic import BaseSettings, Field

from core.logger import LOGGING


class Environments(BaseSettings):
    project_name: str = Field('movies', env='PROJECT_NAME')
    redis_host: str = Field(..., env='REDIS_HOST')
    redis_port: int = Field(6379, env='REDIS_PORT')
    redis_db: int = Field(0, env='REDIS_DB')
    elastic_host: str = Field(..., env='ES_HOST')
    elastic_port: int = Field(9200, env='ES_PORT')
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    origins: list[str] =[
            'http://localhost:80',
        ]


# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

config: Environments | None = None

if not config:
    config = Environments()
