from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from models import Film, FilmDetail
from services.utils import Service
from .qparams import ModelParams
import models.es_query as es_query


class FilmService(Service):
    model = Film
    modelDetail = FilmDetail
    es_index = 'movies'

    def build_search_query(self, params: ModelParams) -> str | None:
        """Основная функция генерации json по модели тела запроса."""
        body = self._build_query_body(params=params)

        if params.dict():

            if not body.query:
                body.query = es_query.Query()
            if not body.query.bool:
                body.query.bool = es_query.QueryBool()
            body.query.bool.must = []

            if params.query:
                match = es_query.match_field(
                    field_name='title',
                    query=params.query
                )
                body.query.bool.must.append(match)

            if params.filter_genre:
                nested = es_query.nested(
                    path = 'genre',
                    field = 'genre_id',
                    value = str(params.filter_genre)
                )
                body.query.bool.must.append(nested)

            if params.filter_genre_name:
                nested = es_query.nested(
                    path = 'genre',
                    field = 'genre_name',
                    value = params.filter_genre_name
                )
                body.query.bool.must.append(nested)

        return body.json(by_alias=True, exclude_none=True)


@lru_cache()
def get_film_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(elastic)
