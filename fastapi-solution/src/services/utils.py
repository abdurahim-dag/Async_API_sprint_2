from abc import ABC
from typing import Any
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError

from models import Film, FilmDetail, Genre, GenreDetail, Person, PersonDetail
import models.es_query as es_query
from .qparams import ModelParams


class Service(ABC):
    """
    Базовый абстрактный класс сервиса доступа к данным в индексе ES.
    Реализована логика получения модели по id и по параметрам запроса.
    В дочерних классах необходима реализация _build_query_order - необходимые поля сортировки.
    """
    model: None
    modelDetail: None
    es_index: str

    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_by_id(self, item_id: UUID) -> FilmDetail | GenreDetail | PersonDetail | None:
        """Функция запрашивает модель по id."""
        try:
            doc = await self.elastic.get(self.es_index, item_id)
        except NotFoundError:
            return None
        return self.modelDetail(**doc['_source'])

    async def get_list(
        self,
        params: ModelParams | Any = None
    ) -> list[Film | Genre | PersonDetail | None] | None:
        """Функция запрашивает список моделей по параметрам запроса."""
        search_query = self.build_search_query(params)
        try:
            docs = await self.elastic.search(index=self.es_index, body=search_query)
        except NotFoundError:
            return None
        return [self.model(**doc['_source']) for doc in docs["hits"]["hits"]]

    def build_search_query(self, params: ModelParams) -> str | None:
        """Основная функция генерации json по модели тела запроса."""
        return self._build_query_body(params=params).json(by_alias=True, exclude_none=True)

    def _build_query_body(self, params: ModelParams) -> es_query.Body:
        """Функция генерации тела запроса.
        Реализованна базовая востребованная для всех моделей логика:
            генерации параметров запроса - фильтр по ID.
        Для работы сортировки необходима реализация _build_query_order,
        которая должна возвращать поле для сортировки.
        """
        body = es_query.Body()

        query = es_query.Query()

        if params.ids:
            query.bool = es_query.QueryBool()

            values = [
                str(_id) for _id in params.ids
            ]
            query.bool.filter = es_query.ids(values=values)

        if params.sort:
            if params.sort.startswith('-'):
                body.sort = [{params.sort[1:]: 'desc'}]
            else:
                body.sort = [{params.sort: 'asc'}]

        if query.bool:
            body.query = query

        body.size = params.page_size
        body.from_ = params.page_num
        return body


    # def _build_query_match(
    #         self,
    #         query: str,
    #         match_field_type: Any,
    #         match_field_name: str,
    # ) -> es_queryy.Match:
    #     match_field_query = es_queryy.MatchFieldQuery(
    #         query=query,
    #     )
    #
    #     match_field = match_field_type(
    #         **{
    #             match_field_name: match_field_query
    #         }
    #     )
    #
    #     return es_queryy.Match(
    #         match=match_field
    #     )
    #
    # def _build_query_bool(self) -> es_queryy.QueryBool:
    #     return es_queryy.QueryBool()
    # #
    # def _build_query_term(
    #         self,
    #         term_field_type: Any,
    #         term_field_name: str,
    #         term_field_value: str,
    # ) -> es_queryy.Term:
    #     term_field = term_field_type(
    #         **{
    #             term_field_name: term_field_value
    #         }
    #     )
    #     return es_queryy.Term(
    #         term=term_field
    #     )
    #
    # def _build_or_get_query_nested(
    #         self,
    #         path: str,
    #         body: es_queryy.ESBodyQuery,
    # ) -> es_queryy.Nested:
    #     """Функция создания структуры nested поискового запроса ES."""
    #     nested = None
    #     if body and body.query and body.query.bool and\
    #        body.query.bool.must:
    #         for el in body.query.bool.must:
    #             if isinstance(el, es_queryy.Nested):
    #                 nested = el
    #
    #     if not nested:
    #         query = self._build_query()
    #         query.bool = self._build_query_bool()
    #
    #         nested_inner = es_queryy.NestedInner(
    #             path=path,
    #             query=query
    #         )
    #         nested = es_queryy.Nested(nested=nested_inner)
    #     return nested
    #
    # def _build_query_bool_must(
    #         self,
    #         body: es_queryy.ESBodyQuery
    # ) -> es_queryy.ESBodyQuery:
    #     if not body.query.bool:
    #         body.query.bool = self._build_query_bool()
    #     if not body.query.bool.must:
    #         body.query.bool.must = []
    #     return body
