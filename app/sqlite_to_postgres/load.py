"""Модуль загрузки csv файла в таблицу."""
import logging
from contextlib import closing
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

from sqlite_to_postgres.logger import logger
from sqlite_to_postgres.utils import get_str_path


class Load:
    """
    Класс отвечающий за загрузку.
    """

    def __init__(
            self,
            conn_params: dict,
            schema: str,
            upload_path: Path
    ) -> None:
        """Устанавливаем целевые параметры соединения и схему БД.

        Args:
            conn_params (dict): Параметры соединения с БД.
            schema (str): Схема БД.
            upload_path (Path): Путь до папки, откуда брать данные.
        """
        self.url = URL.create(**conn_params)
        self.schema = schema
        self.upload_path = upload_path

    def upload(self, csv_file_name: str, table_name: str) -> None:
        """Загружаем пачками строки из файла в таблицу.

        Args:
            csv_file_name (str): Загружаемый файл csv.
            table_name (str): Целевая таблица, для загрузки.
        """
        csv_path = get_str_path(csv_file_name, self.upload_path)
        df = pd.read_csv(csv_path)
        with closing(create_engine(self.url).connect()) as conn:
            # Очищаем таблицу.
            conn.execute(f"truncate {self.schema + '.' + table_name} cascade;")
            # Если строк в файле 0, то идём дальше.
            count = df.shape[0]
            if count > 0:
                i = 0
                step = int(count / 100)
                if step == 0:
                    step = count
                # До опустошения загружаем стоки из файла в таблицу.
                while i <= count:
                    chunk = df.loc[i:i + step]
                    num_rows = chunk.to_sql(
                        con=conn,
                        name=table_name,
                        if_exists='append',
                        index=False,
                        method='multi',
                        schema=self.schema,
                    )
                    logging.info("Number of rows is added: %s", num_rows)
                    i += step + 1
        logger.info("File %s completed load to table %s", csv_file_name, table_name)
