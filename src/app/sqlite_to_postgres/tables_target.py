"""
Модуль описывающий структуру таблиц
целевой БД, посредством dataclass.
"""
from dataclasses import dataclass
from uuid import UUID

from pendulum import DateTime


@dataclass(frozen=True)
class FilmWork:
    id: UUID
    title: str
    type: str
    description: str = None
    rating: str = None
    creation_date: DateTime = None
    created: DateTime = None
    modified: DateTime = None


@dataclass(frozen=True)
class Genre:
    id: UUID
    name: str
    description: str = None
    created: DateTime = None
    modified: DateTime = None


@dataclass(frozen=True)
class Person:
    id: UUID
    full_name: str
    created: DateTime = None
    modified: DateTime = None


@dataclass(frozen=True)
class PersonFilmWork:
    id: UUID
    film_work_id: UUID
    person_id: UUID
    role: str
    created: DateTime = None


@dataclass(frozen=True)
class GenreFilmWork:
    id: UUID
    film_work_id: UUID
    genre_id: UUID
    created: DateTime = None
