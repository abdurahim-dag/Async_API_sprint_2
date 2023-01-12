from pathlib import Path, PurePath

from pydantic import BaseSettings, BaseModel, Field


class TestSettings(BaseSettings):
    """Общие настройки, для всех тетов."""
    es_host: str = Field(default='127.0.0.1', env='ES_HOST')
    es_port: str = Field(default='9200', env='ES_PORT')
    redis_host: str = Field(default='127.0.0.1', env='REDIS_HOST')
    redis_port: str = Field(default='6379', env='REDIS_PORT')
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


class TestESIndexSettings(BaseModel):
    """Модель настроек, для конкретного индекса."""
    index_name: str
    schema_file_path: Path
    data_file_path: Path


test_settings = TestSettings()

film_test_settings = TestESIndexSettings(
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

genre_test_settings = TestESIndexSettings(
    index_name='genre',
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

person_test_settings = TestESIndexSettings(
    index_name='person',
    schema_file_path=Path(
        PurePath(
            'testdata',
            'es_schema_persons.json'
        )
    ),
    data_file_path=Path(
        PurePath(
            'testdata',
            'persons.json'
        )
    )
)