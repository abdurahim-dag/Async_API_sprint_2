from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from models import Genre, GenreDetail
from services.utils import Service
from .qparams import ModelParams


class GenreService(Service):
    model = Genre
    modelDetail = GenreDetail
    es_index = 'genres'

    def build_search_query(self, params: ModelParams | None) -> None:
        body = self._build_query_body(params=params)
        return body.json(by_alias=True, exclude_none=True, exclude_defaults=True)


@lru_cache()
def get_genre_service( elastic: AsyncElasticsearch = Depends(get_elastic),
                      ) -> GenreService:
    return GenreService(elastic)
