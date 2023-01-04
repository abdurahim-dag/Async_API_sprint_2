import json
import pathlib

from .base import BaseStorage
from .utils import DateEncoder


class JsonFileStorage(BaseStorage):
    def __init__(self, path_to_file: str):
        self.file_path = pathlib.Path(path_to_file)
        if not self.file_path.exists():
            with open(self.file_path, 'w', encoding='utf8') as f:
                f.write('{}')
        if not self.file_path.is_file():
            raise Exception("Указанный, как файл, json хранилище состояния, это папка!")

    def save_state(self, state: dict):
        with open(self.file_path, 'w', encoding='utf8') as f:
            json.dump(state, f, cls=DateEncoder)

    def retrieve_state(self) -> dict:
        with open(self.file_path, 'r', encoding='utf8') as f:
            state = json.load(f)
        return state
