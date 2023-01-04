from uuid import UUID

from pydantic import BaseModel, Field


class UUIDMixin(BaseModel):
    id: UUID = Field(alias='uuid')

    class Config:
        allow_population_by_field_name = True


