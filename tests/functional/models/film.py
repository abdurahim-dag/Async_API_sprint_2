from .mixin import UUIDMixin
from .genre import Genre
from .person import Person


class Film(UUIDMixin):
    title: str
    imdb_rating: float | None


class FilmDetail(Film):
    description: str | None = ''
    actor_names: list[str] = []
    writer_names: list[str] = []
    genre: list[Genre] = []
    actors: list[Person] = []
    writers: list[Person] = []
    directors: list[Person] = []


