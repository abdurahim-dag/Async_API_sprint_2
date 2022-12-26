import abc
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class OrderEnum(str, Enum):
     ASC: str
     DESC: str

class ModelParams(BaseModel, abc.ABC):
    sort: OrderEnum | None
    page_num: int | None
    page_size: int | None
    filter_genre: UUID | None
    filter_genre_name: str | None
    query: str | None
    ids: list[UUID] | None