"""
Модуль описывающий структуру таблицы-источника
БД, посредством dataclass.
"""
from dataclasses import dataclass

from pendulum import Date
from pendulum import DateTime


@dataclass(frozen=True)
class FilmWork:
    id: str
    title: str
    type: str
    description: str = None
    rating: float = None
    creation_date: Date = None
    created_at: DateTime = None
    updated_at: DateTime = None


@dataclass(frozen=True)
class Genre:
    id: str
    name: str
    description: str = None
    created_at: DateTime = None
    updated_at: DateTime = None


@dataclass(frozen=True)
class Person:
    id: str
    full_name: str
    created_at: DateTime = None
    updated_at: DateTime = None


@dataclass(frozen=True)
class PersonFilmWork:
    id: str
    film_work_id: str
    person_id: str
    role: str
    created_at: DateTime = None


@dataclass(frozen=True)
class GenreFilmWork:
    id: str
    film_work_id: str
    genre_id: str
    created_at: DateTime = None
