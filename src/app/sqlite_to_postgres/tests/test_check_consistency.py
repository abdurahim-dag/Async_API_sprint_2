import dataclasses
import os
import sqlite3
from contextlib import closing
from dataclasses import Field
from pathlib import Path
from pathlib import PurePath
from typing import Any
from typing import Callable
from typing import Generator
from typing import Type
from typing import Union

import psycopg2
import pytest
from dotenv import load_dotenv
from pendulum import DateTime
from pendulum import parse

from sqlite_to_postgres import tables_target
from sqlite_to_postgres.map_tables import map_tables

TargeDataclasses = Union[
    tables_target.FilmWork,
    tables_target.Genre,
    tables_target.Person,
    tables_target.PersonFilmWork,
    tables_target.GenreFilmWork,
]


class TestDB:
    """
    Pytest класс проверки на равенства значений и количества строк в таблицах.
    """
    @pytest.fixture
    def init(self) -> None:
        """Фикстура для инициализации начальных значений.

        Raises:
            FileExistsError: Если нет файла БД sqlite.
        """
        load_dotenv()
        conn_params = {
            'database': os.environ.get('PG_DB_NAME', 'postgres'),
            'user': os.environ.get('PG_USER', 'postgres'),
            'password': os.environ.get('PG_PASSWORD', 'postgres'),
            'host': os.environ.get('PG_HOST', 'localhost'),
            'port': os.environ.get('PG_PORT', 'postgres'),
        }
        # Проверка наличия файла БД sqlite выше в иерархии.
        schema = os.environ.get('PG_SCHEMA', 'public')

        db_name = os.environ.get('SQLITE_DB_PATH', 'db.sqlite')
        data_dir = os.environ.get('DATA_DIR', '.data')
        db_sqlite_path = Path(
            PurePath(Path(data_dir)),
            db_name,
        )
        if not db_sqlite_path.exists():
            raise FileExistsError

        self.conn_params = conn_params
        self.db_path = str(db_sqlite_path)
        self.map_tables = map_tables
        self.sql_count = 'select count(*) from {table};'
        self.sql_all = 'select {columns} from {table};'
        self.sql_byid = "select {columns} from {table} where id='{id}';"
        self.schema = schema

    @pytest.fixture
    def db_connect(self, init: Callable) -> Generator[None, None, None]:
        """Фиксутра, для нормального открытия и закрытия соединений в БД.

        Args:
            init(Callable): Выше стоящая фикстура инициализации.

        Yields:
            Generator[None]: Точка выхода для корректного завершения подключения.
        """
        with closing(psycopg2.connect(**self.conn_params)) as pg_conn:
            with closing(pg_conn.cursor()) as self.pg_curs:
                with closing(sqlite3.connect(self.db_path)) as sqlite_conn:
                    with closing(sqlite_conn.cursor()) as self.sqlite_curs:
                        yield


    def get_dc(
            self,
            row: tuple,
            fields: tuple[Field, ...],
            dc: Type[TargeDataclasses]) -> TargeDataclasses:
        """Функция формирует Dataclass

        Args:
            row (tuple): Кортеж значений строки таблицы.
            fields (list[Field]): Поля даткласса.
            dc (Type[TargeDataclasses]): Даткласс таблицы.

        Returns:
            Type[TargeDataclasses]: Заполненный датакласс.

        """
        fields_list = [field.name for field in fields]
        kwargs = dict(zip(fields_list, row))
        return dc(**kwargs)


    def test_tables_counts(self, db_connect: Callable) -> None:
        """Тест совпадения количества строк в таблицах sqlite и PG.

        Args:
            db_connect(Callable): Фикстура настройки соединения БД.
        """
        # Словарь куда будем складывать ошибки.
        check = []
        for table in self.map_tables:
            # Запрашиваем количество строк таблицы PG.
            sql = self.sql_count.format(table=table[0])
            self.pg_curs.execute(sql)
            row = self.pg_curs.fetchone()
            count_pg = int(row[0])

            # Запрашиваем количество строк таблицы sqlite.
            self.sqlite_curs.execute(sql)
            row = self.sqlite_curs.fetchone()
            count_sqlite = int(row[0])

            # Если количество строк не совпали - ошибку в список.
            if count_sqlite != count_pg:
                check.append(f"{table[0]}: PG({count_pg}) sqlite({count_sqlite})")
        assert not check, '|'.join(check)


    def get_typed_value(self, field: Field, dc: TargeDataclasses) -> Any:
        """Функция привидения поля датакласса к установленному.

        Args:
            field (Field): Поле приводимого дата класса.
            dc (TargeDataclasses): Датакласс.

        Returns:
            Any: Значения поля приведенное к
            установленному типу
            в датаклассе.
        """
        value = getattr(dc, field.name)
        if bool(value):
            value = str(value)
            if field.type is DateTime:
                value = parse(value)
            else:
                value = field.type(value)
        return value

    def test_tables_row(self, db_connect: Callable) -> None:
        """ Тест проверки на свопадение значений в строках
            таблиц sqlite и PG.

        Args:
            db_connect (Callable): Фикстура предварительной
                настройки БД.
        """
        checks = []
        for table in self.map_tables:
            table_name = table[0]
            dataclass_pg = table[1]
            dataclass_sqlite = table[2]

            # Заполняем строки со списком столбцов в таблицах.
            fields_dc_pg = dataclasses.fields(dataclass_pg)
            fields_dc_sqlite = dataclasses.fields(dataclass_sqlite)
            columns_pg = ','.join([field.name for field in fields_dc_pg])
            columns_sqlite = ','.join([field.name for field in fields_dc_sqlite])

            # Проходим все записи в таблице sqlite.
            sql = self.sql_all.format(columns=columns_sqlite, table=table_name)
            self.sqlite_curs.execute(sql)
            for row_sqlite in self.sqlite_curs:
                dc_sqlite = self.get_dc(row_sqlite, fields_dc_pg, dataclass_pg)

                # Находим строку с таким же id.
                sql = self.sql_byid.format(columns=columns_pg, table=table_name, id=row_sqlite[0])
                self.pg_curs.execute(sql)
                row_pg = self.pg_curs.fetchone()
                if not row_pg:
                    checks.append(f"{table_name}(id): pg(Not found), sqlite({row_sqlite[0]})")
                    continue

                # Заполняем датакласс из полученной строки и проверяем.
                dc_pg = self.get_dc(row_pg, fields_dc_pg, dataclass_pg)
                for field in fields_dc_pg:
                    value_pg = self.get_typed_value(field, dc_pg)
                    value_sqlite = self.get_typed_value(field, dc_sqlite)
                    if value_pg != value_sqlite:
                        checks.append(f"{table_name}({field.name}): pg({value_pg}), sqlite({value_sqlite})")
        assert not checks, ' | '.join(checks)
