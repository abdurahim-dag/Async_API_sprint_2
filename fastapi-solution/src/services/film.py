from functools import lru_cache

import models.es_query as es_query
from db.elastic import get_elastic
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models import Film, FilmDetail
from services.utils import Service

from .qparams import ModelParams


class FilmService(Service):
    model = Film
    modelDetail = FilmDetail
    es_index = 'movies'

    def build_search_query(self, params: ModelParams) -> str | None:
        """Основная функция генерации json по модели тела запроса."""
        body = self._build_query_body(params=params)
        query = body.query
        b = query.bool

        if params.query:
            match = es_query.match_field(
                field_name='title',
                query=params.query
            )
            b.must.append(match)

        if params.filter_genre or params.filter_genre_name:
            nested = es_query.nested(
                path = 'genre'
            )
            b.must.append(nested)
            nested_bool = nested.nested.query.bool

            if params.filter_genre:
                term = es_query.Term(
                    term = {'genre.id': params.filter_genre}
                )
                nested_bool.filter.append(term)

            if params.filter_genre_name:
                match = es_query.match_field(
                    field_name='genre.name',
                    query=str(params.filter_genre_name)
                )
                nested_bool.must.append(match)

        return body.json(by_alias=True, exclude_none=True, exclude_defaults=True)


@lru_cache()
def get_film_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(elastic)
