"""Модуль выгрузки данных из БД sqlite и заданной таблицы."""
import csv
import dataclasses
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Union

from sqlite_to_postgres.logger import logger
from sqlite_to_postgres.tables_target import FilmWork
from sqlite_to_postgres.tables_target import Genre
from sqlite_to_postgres.tables_target import GenreFilmWork
from sqlite_to_postgres.tables_target import Person
from sqlite_to_postgres.tables_target import PersonFilmWork
from sqlite_to_postgres.utils import get_str_path


class Extract:
    """
    Класс выгружает данные из таблицы, как есть.
    """
    def __init__(
            self,
            db_path: str,
            extract_path: Path,
    ) -> None:
        """Конструктор класса.

        Args:
            db_path (str): Путь до БД sqlite.
            extract_path (Path): Путь до папки, куда сохранять данные.
        """
        self.sql = 'select {columns} from {table};'
        self.sql_count = 'select count(*) from {table};'
        self.extract_path = extract_path
        self.db_path = get_str_path(db_path, extract_path)

    def extract(
        self,
        table_name: str,
        dataclass: Union[FilmWork, Genre, Person, PersonFilmWork, GenreFilmWork],
        csv_filename: str,
    ) -> None:
        """Функция выгрузки таблицы из БД в файл csv.

        Args:
            table_name (str): название таблицы.
            dataclass (dataclass): Описание структуры целевой таблицы.
            csv_filename (str): название файла csv, куда будем выгружать.
        """
        csv_path = get_str_path(csv_filename, self.extract_path)
        columns = [field.name for field in dataclasses.fields(dataclass)]
        columns_str = ','.join(columns)
        with closing(sqlite3.connect(self.db_path)) as conn:
            with closing(conn.cursor()) as curs:
                # Если строк в таблице 0, то идём дальше.
                exec_sql = self.sql_count.format(table=table_name)
                curs.execute(exec_sql)
                count = int(curs.fetchone()[0])
                if count > 0:
                    # Записываем как есть данные в файл csv.
                    with closing(open(csv_path, 'w', encoding="utf-8", newline='')) as f:
                        writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
                        exec_sql = self.sql.format(columns=columns_str, table=table_name)
                        curs.execute(exec_sql)
                        i = 0
                        step = int(count / 100)
                        if step == 0:
                            i = count
                            step = count
                        writer.writerow(columns)
                        while i <= count:
                            rows = curs.fetchmany(step)
                            writer.writerows(rows)
                            i += step
                        logger.info("Extracted %s rows of table %s", count, table_name)
