from uuid import UUID

from pydantic import Field

from .config import OrjsonConfigMixin, UUIDMixin


class Person(UUIDMixin, OrjsonConfigMixin):
    name: str = Field(alias='full_name')

    class Config:
        allow_population_by_field_name = True


class PersonDetail(Person):
    role: str
    film_ids: list[UUID] = []
