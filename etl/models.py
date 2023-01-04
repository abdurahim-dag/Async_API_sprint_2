from pathlib import Path
from uuid import UUID
from typing import Any

from pendulum import Date
from pydantic import (
    BaseModel,
    Field,
    validator,
    BaseSettings,
)
from typing import Any

# TODO: ADD PostgresDsn

class UUIDMixin(BaseModel):
    id: UUID

class GenreName(UUIDMixin):
    name: str

class Genre(GenreName):
    description: str


class PersonName(UUIDMixin):
    name: str


class Person(UUIDMixin):
    full_name: str
    role: str
    film_ids: list[str] | None


class Movie(UUIDMixin):
    imdb_rating: float
    genre: list[GenreName]

    title: str
    description: str | None

    directors: list[PersonName]
    actors: list[PersonName]
    writers: list[PersonName]

    actors_names: list[str] | None
    writers_names: list[str] | None

    @validator('imdb_rating')
    def name_must_contain_space(cls, v):
        if v < 0:
            v = 0
        elif v > 100:
            v = 100
        return v


class ESIndex(BaseModel):
    id: UUID = Field(None, alias="_id")
    index: str = Field(None, alias="_index")


class ESIndexLine(BaseModel):
    index: ESIndex


class EtlState(BaseModel):
    date_from: Date | None
    date_to: Date | None
    step: int | None


class ExtractSettings(BaseModel):
    conn_params: dict
    schemas: str
    extract_path: Path
    sql_file: Path
    batches: int


class TransformSettings(BaseModel):
    transform_path: Path
    extract_path: Path
    index_name: str
    model: Any


class LoadSettings(BaseModel):
    conn_str: str
    index_name: str
    transform_path: Path
    schema_file_path: Path


class Environments(BaseSettings):
    pg_db_name: str
    pg_user: str
    pg_password: str
    pg_host: str
    pg_port: str
    pg_schema: str
    batches: int
    extract_data_dir: str
    sql_dir: str

    transform_data_dir: str
    es_host: str
    es_port: str

    es_settings_path: str

    class Config:
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> Any:
            if field_name in ['sql_extract_file_names','es_indexes', ]:
                return [x for x in raw_val.split(',')]
            return cls.json_loads(raw_val)