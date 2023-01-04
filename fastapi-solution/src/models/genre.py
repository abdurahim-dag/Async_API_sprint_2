from .config import UUIDMixin, OrjsonConfigMixin


class Genre(UUIDMixin, OrjsonConfigMixin):
    name: str


class GenreDetail(Genre):
    description: str | None = ''

