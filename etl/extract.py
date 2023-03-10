import json
from contextlib import closing
from pathlib import PurePath

import psycopg2

from backoff import on_exception
from logger import logger
from models import ExtractSettings
from state import State


class PostgresExtractor:
    """Extract batches rows to files."""
    def __init__(
            self,
            settings: ExtractSettings,
            state: State,
            index_name: str,
    ) -> None:
        self.settings = settings
        self.state = state
        self.index_name = index_name


    @on_exception(
        exception=psycopg2.DatabaseError,
        start_sleep_time=1,
        factor=2,
        border_sleep_time=15,
        max_retries=15,
        logger=logger,
    )
    def extract(self):
        """Extract rows to files."""
        with closing(
                psycopg2.connect(**self.settings.conn_params)
        ) as conn:
            with closing(conn.cursor()) as curs:

                state = self.state.get_state()

                sql = open(self.settings.sql_file, encoding='utf-8').read()
                sql = sql.format(
                    date_from=state.date_from,
                    date_to=state.date_to,
                    from_schema=self.settings.schemas,
                    offset=state.step,
                )
                curs.execute(sql)

                while rows := curs.fetchmany(self.settings.batches):
                    if len(rows) == 0:
                        break

                    file_name = f"{self.index_name}-{state.date_to}-{state.step}.json"
                    file_path = PurePath(self.settings.extract_path, file_name)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(rows, f)

                    # Сохраняем каждый выполненный шаг.
                    state.step += 1
                    self.state.set_state(state)
                    logger.info("Extracted file %s", file_name)

                # Сохраним step < 0.
                # Установим дату началу, следующего запуска со вчера.
                # И следующий запуск начнётся со вчерашней даты.
                state.step = -1
                state.date_from = state.date_to
                self.state.set_state(state)
