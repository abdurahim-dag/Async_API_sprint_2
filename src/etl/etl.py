import os
from pathlib import Path

import pendulum

from models import ExtractSettings, LoadSettings, TransformSettings, Movie, Genre
from state import State
from extract import PostgresExtractor
from load import Load
from transform import DataTransform


class EtlProcessing:

    file_status = '.RUNING'

    def __init__(
            self,
            state: State,
            extract_settings: ExtractSettings,
            load_settings: LoadSettings,
            transform_settings: TransformSettings,
            state_key: str,
    ):

        self._check_run_status()
        self._set_run_status()

        self.load_settings = load_settings
        self.extract_settings = extract_settings
        self.transform_settings = transform_settings

        self.state = state
        self.state_key = state_key

    def _set_run_status(self):
        """Set flag started etl process."""
        open(self.file_status, 'w').close()

    def _check_run_status(self):
        """Raise if other etl process started."""
        path = Path(self.file_status)
        if path.exists():
            raise Exception('Параллельно работает такой же процесс!')

    def _init_state_step(self) -> None:
        """ Функция инициализации состояния процесса name.
        Если состояние ранее не сохранялось, то выгружаем всё по вчера.
        Если step < 0, то значит предыдущий этап успешно закончился.
        Тогда, устанавливаем дату выгрузки по вчера.
        Не сбиваем сохранённое состояние, если step > 0!

        """
        state = self.state.get_state()
        if state.step is None:
            state.step = 0
            state.date_from = pendulum.parse('1900-01-01', exact=True)
            state.date_to = pendulum.yesterday('UTC').date()
        elif state.step < 0:
            state.step = 0
            state.date_to = pendulum.yesterday('UTC').date()
        self.state.set_state(state)

    def extract(self):
        self._init_state_step()
        extracter = PostgresExtractor(
            settings=self.extract_settings,
            state=self.state,
        )
        extracter.extract()

    def transform(self):
        # Передача настроек и трасф-й модели
        trancformer = DataTransform(
            settings=self.transform_settings,
        )
        trancformer.transform()

    def load(self):
        load = Load(
            self.load_settings,
        )
        load.load()

    def main(self):
        self.extract()
        self.transform()
        self.load()
        os.remove(self.file_status)
