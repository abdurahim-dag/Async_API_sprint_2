"""
Модуль описывающий посредством кортежей:
первый вложенный кортеж - имена таблиц, совпадают с источником и целевой БД;
второй вложенный кортеж - структура целевой БД(dataclass);
третий вложенный кортеж - структура БД источника(dataclass).
"""
import sqlite_to_postgres.tables_target as tables_target
import sqlite_to_postgres.tables_source as tables_source

map_tables = (
    (
        'film_work',
        tables_target.FilmWork,
        tables_source.FilmWork,
    ),
    (
        'genre',
        tables_target.Genre,
        tables_source.Genre,
    ),
    (
        'person',
        tables_target.Person,
        tables_source.Person,
    ),
    (
        'genre_film_work',
        tables_target.GenreFilmWork,
        tables_source.GenreFilmWork,
    ),
    (
        'person_film_work',
        tables_target.PersonFilmWork,
        tables_source.PersonFilmWork,
    )
)
