"""Модуль утилит."""
import re
from pathlib import Path
from pathlib import PurePath


def file_rename(name: str, sufix: str) -> str:
    """Функция переименования имени файоа по шаблону.

    Args:
        name (str): Имя файла.
        sufix (str): Добавочный суффикс к файлу.

    Returns:
        str: Имя файла с добавлением суффикса.
    """
    m = re.search('(.+)(\..+$)', name)
    new_name = m[1] + '_' + sufix + m[2]
    return new_name


def get_str_path(file_name: str, path: Path) -> str:
    """Генератор пути до файла.

    Args:
        file_name (str): Имя файла.
        path (Path): Путь до папки, где будет файл.

    Returns:
        str: Путь до файла.
    """
    result = Path(
        PurePath(
            Path(path),
            file_name,
        ),
    )
    return str(result)
