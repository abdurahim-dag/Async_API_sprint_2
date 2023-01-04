from .mixin import UUIDMixin


class Genre(UUIDMixin):
    name: str


class GenreDetail(Genre):
    description: str | None = ''

