"""
Модуль с описанием моделей используемых в генерации json
тела запроса для ES.
Пример используемого запроса представлен в файле es_query_example.json
Ниже в описаниях к классам указано, где в json расположена модель:
    <элемент предок в json>
"""
from enum import Enum
from typing import ForwardRef

import orjson
from pydantic import BaseModel, Field


# Значения сортировки
class OrderEnum(str, Enum):
    ASC = 'asc'
    DESC = 'desc'


# Значения фильтрации по id
class FieldId(BaseModel):
    id: str


# Сортировка поиска
class FieldFilmRating(BaseModel):
    """sort: ..."""
    imdb_rating: OrderEnum


# Внутренности, для полей поиска.
class MatchFieldQuery(BaseModel):
    """[field_name]: ..."""

    query: str
    fuzziness: str = Field(default='AUTO')


# Поле поиска
class TitleField(BaseModel):
    """match: ..."""

    title: MatchFieldQuery


# Поле поиска
class FullNameField(BaseModel):
    """match: ..."""

    full_name: MatchFieldQuery


# Представление поля name, для модели genre
class FieldGenreName(BaseModel):
    """match: ..."""

    genre_name: MatchFieldQuery = Field(alias='genre.name')

    class Config:
        allow_population_by_field_name = True


# Поле match
class Match(BaseModel):
    """must: ..."""
    match: TitleField | FullNameField | FieldGenreName


# Представление поля id, для модели genre
class FieldGenreID(BaseModel):
    """term: ..."""

    genre_id: str = Field(alias='genre.id')

    class Config:
        allow_population_by_field_name = True


# Поле term
class Term(BaseModel):
    """filter: ..."""

    term: FieldGenreID


# Поиск по id в filter
class IDSValues(BaseModel):
    """ids: ..."""

    values: list[str] = []


# Поиск по id в filter
class IDS(BaseModel):
    """filter: ..."""
    ids: IDSValues


QueryRef = ForwardRef("Query")


# Поиск по вложенные полям.
class NestedInner(BaseModel):
    """nested: ..."""
    path: str
    query: QueryRef


# Поиск по вложенные полям.
class Nested(BaseModel):
    """must: ..."""
    nested: NestedInner


class QueryBool(BaseModel):
    """bool: ..."""
    must: list[Match | Nested] | None
    filter: Term | IDS | None


class Query(BaseModel):
    """query: ..."""
    bool: QueryBool | None


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class ESBodyQuery(BaseModel):
    """Корневой элемент поиска."""
    query: Query | None
    sort: FieldFilmRating | FieldId | None
    size: int = Field(default=0)
    from_: int = Field(default=0, alias='from')

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


NestedInner.update_forward_refs()
