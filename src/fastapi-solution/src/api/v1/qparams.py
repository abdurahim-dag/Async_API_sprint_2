"""Модели для параметров запросов."""
from enum import Enum
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field


class OrderEnum(str, Enum):
    ASC: str
    DESC: str


class imbdbOrderEnum(OrderEnum):
    ASC = 'imdb_rating'
    DESC = '-imdb_rating'


class idPersonOrderEnum(OrderEnum):
    ASC = 'id'
    DESC = '-id'


class CommonParams(BaseModel):
    sort: imbdbOrderEnum | idPersonOrderEnum | None = Field(Query(
        default=None,
        description='Сортировка по указанному полю.',
    ))
    page_num: int | None = Field(Query(
        default=0,
        alias='page[number]',
        gte=0,
        description='Номер страницы.',
    ))
    page_size: int | None = Field(Query(
        default=25,
        alias='page[size]',
        gt=0,
        lte=50,
        description='Количество элементов на странице.',
    ))
    query: str | None = Field(Query(
        default=None,
        description='Текст полнотекстового поиска.',
    ))
    ids: list[UUID] | None = Field(Query(
        default=None,
        description='Список id\'s фильмов, для фильтрации.',
    ))


class FilmParams(CommonParams):
    filter_genre: UUID | None = Field(Query(
        default=None,
        alias='filter[genre]',
        description='Фильтр по id жанра.',
    ))
    filter_genre_name: str | None = Field(Query(
        default=None,
        alias='filter[genre.name]',
        description='Фильтр по названию жанра.',
    ))
