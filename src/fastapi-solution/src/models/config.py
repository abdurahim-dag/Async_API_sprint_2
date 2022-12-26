from uuid import UUID

import orjson
from pydantic import BaseModel, Field


class UUIDMixin(BaseModel):
    id: UUID = Field(alias='uuid')

    class Config:
        allow_population_by_field_name = True


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class OrjsonConfigMixin(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
