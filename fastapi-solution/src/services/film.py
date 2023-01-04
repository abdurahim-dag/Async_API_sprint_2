from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from models import es_query, Film, FilmDetail
from services.utils import Service
from .qparams import ModelParams


class FilmService(Service):
    model = Film
    modelDetail = FilmDetail
    es_index = 'movies'

    def build_search_query(self, params: ModelParams) -> str | None:
        """Основная функция генерации json по модели тела запроса."""
        body = self._build_query_body(params=params)

        if params.query:
            body = self._build_query_bool_must(body)

            match = self._build_query_match(
                query=params.query,
                match_field_type=es_query.TitleField,
                match_field_name='title'
            )

            body.query.bool.must.append(
                match
            )

        if params.filter_genre:
            body = self._build_query_bool_must(body)

            nested = self._build_or_get_query_nested(
                path='genre',
                body=body,
            )

            term = self._build_query_term(
                term_field_type=es_query.FieldGenreID,
                term_field_name='genre_id',
                term_field_value=str(params.filter_genre)
            )

            nested.nested.query.bool.filter = term

            body.query.bool.must.append(nested)

        if params.filter_genre_name:
            body = self._build_query_bool_must(body)

            nested = self._build_or_get_query_nested(
                path='genre',
                body=body,
            )

            match = self._build_query_match(
                query=str(params.filter_genre_name),
                match_field_type=es_query.FieldGenreName,
                match_field_name='genre_name'
            )

            if nested.nested.query.bool.must:
                nested.nested.query.bool.must.append(match)
            else:
                nested.nested.query.bool.must = [match]

            body.query.bool.must.append(nested)

        return body.json(by_alias=True, exclude_none=True)

    def _build_query_order(self, order: es_query.OrderEnum) -> es_query.FieldFilmRating:
        """Функция генерации модели, для поля сортировки."""
        return es_query.FieldFilmRating(
            imdb_rating=order
        )


@lru_cache()
def get_film_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(elastic)
