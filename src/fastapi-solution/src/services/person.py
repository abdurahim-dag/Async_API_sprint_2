from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from models import es_query, PersonDetail
from services.utils import Service
from .qparams import ModelParams


class PersonService(Service):
    model = PersonDetail
    modelDetail = PersonDetail
    es_index = 'persons'

    def build_search_query(self, params: ModelParams) -> str | None:
        """Основная функция генерации json по модели тела запроса."""
        body = self._build_query_body(params=params)

        if params.query:
            body = self._build_query_bool_must(body)

            match = self._build_query_match(
                query=params.query,
                match_field_type=es_query.FullNameField,
                match_field_name='full_name'
            )

            body.query.bool.must.append(
                match
            )

        return body.json(by_alias=True, exclude_none=True)

    def _build_query_order(self, order: es_query.OrderEnum) -> es_query.FieldId:
        """Функция генерации модели, для поля сортировки."""
        return es_query.FieldId(
            id=order
        )


@lru_cache()
def get_person_service(elastic: AsyncElasticsearch = Depends(get_elastic), ) -> PersonService:
    return PersonService(elastic)
