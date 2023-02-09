from pathlib import Path, PurePath

from pydantic import BaseSettings, BaseModel, Field


class CommonSettings(BaseSettings):
    """Общие настройки, для всех тестов."""
    es_host: str = Field(default='127.0.0.1', env='ES_HOST')
    es_port: str = Field(default='9200', env='ES_PORT')

    redis_host: str = Field(default='127.0.0.1', env='REDIS_HOST')
    redis_port: str = Field(default='6379', env='REDIS_PORT')
    redis_db: str = Field(default='0', env='REDIS_DB')

    api_host: str = Field(default='127.0.0.1', env='API_HOST')
    api_port: str = Field(default='8080', env='API_PORT')

    @property
    def es_conn_str(self) -> str:
        return f"http://{self.es_host}:{self.es_port}"

    @property
    def redis_conn_str(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}"

    @property
    def api_endpoint_films(self) -> str:
        return f"http://{self.api_host}:{self.api_port}/api/v1/films/"

    @property
    def api_endpoint_genres(self) -> str:
        return f"http://{self.api_host}:{self.api_port}/api/v1/genres/"


class ESIndexSettings(BaseModel):
    """Модель настроек, для конкретного индекса."""
    index_name: str
    schema_file_path: Path
    data_file_path: Path


settings = CommonSettings()

film_index = ESIndexSettings(
    index_name='movies',
    schema_file_path=Path(
        PurePath(
            'testdata',
            'es_schema_movies.json'
        )
    ),
    data_file_path=Path(
        PurePath(
            'testdata',
            'movies.json'
        )
    )
)

genre_index = ESIndexSettings(
    index_name='genres',
    schema_file_path=Path(
        PurePath(
            'testdata',
            'es_schema_genres.json'
        )
    ),
    data_file_path=Path(
        PurePath(
            'testdata',
            'genres.json'
        )
    )
)
