from pydantic import BaseModel, Field
from .query import Query
import orjson


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Body(BaseModel):
    """Корневой элемент поиска."""
    query: Query = Query()
    sort: list = []
    size: int = Field(default=-1)
    from_: int = Field(default=-1, alias='from')

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps

