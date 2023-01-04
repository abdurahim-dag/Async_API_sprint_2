from models import EtlState
from storage.base import BaseStorage


class State:
    """
    Класс для хранения состояния при работе с данными, чтобы постоянно не перечитывать данные с начала.
    Здесь представлена реализация с сохранением состояния в файл.
    В целом ничего не мешает поменять это поведение на работу с БД или распределённым хранилищем.
    """

    def __init__(self,
                 storage: BaseStorage,
                 key: str,
        ):
        self.storage = storage
        self.key = key

    def set_state(self, value: EtlState) -> None:
        """Установить состояние для определённого ключа"""
        values = self.storage.retrieve_state()
        values[self.key] = value.dict()
        self.storage.save_state(values)

    def get_state(self) -> EtlState:
        """Получить состояние по определённому ключу"""
        values = {self.key: {}}
        values.update(self.storage.retrieve_state())
        state = EtlState(**values.get(self.key))
        return state
