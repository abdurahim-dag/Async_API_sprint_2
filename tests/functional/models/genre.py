from .mixin import UUIDMixin
from pydantic import Field


class Genre(UUIDMixin):
    name: str = Field(alias='name')

    class Config:
        allow_population_by_field_name = True

class GenreDetail(Genre):
    name: str