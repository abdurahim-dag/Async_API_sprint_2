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
        query = body.query
        b = query.bool

        if params.query:
            match = es_query.match_field(
                field_name='full_name',
                query=params.query
            )
            b.must.append(match)

        return body.json(by_alias=True, exclude_none=True, exclude_defaults=True)



@lru_cache()
def get_person_service(elastic: AsyncElasticsearch = Depends(get_elastic), ) -> PersonService:
    return PersonService(elastic)
