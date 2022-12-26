from abc import ABC
from typing import Any
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError

from models import es_query, Film, FilmDetail, Genre, GenreDetail, Person, PersonDetail
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
        return await self._get_item_from_elastic(item_id)

    async def get_list(
        self,
        params: ModelParams | Any = None
    ) -> list[Film | Genre | PersonDetail | None]:
        """Функция запрашивает список моделей по параметрам запроса."""
        search_query = self.build_search_query(params)
        return await self._get_items_from_elastic(search_query)

    async def _get_item_from_elastic(self, item_id: UUID) -> FilmDetail | GenreDetail | PersonDetail | None:
        """Запрос в индекс ES по id doc."""
        try:
            doc = await self.elastic.get(self.es_index, item_id)
        except NotFoundError:
            return None
        return self.modelDetail(**doc['_source'])

    async def _get_items_from_elastic(self, query_body) -> list[Film | Genre | Person | None] | None:
        """Запрос в индекс ES по телу запроса."""
        try:
            docs = await self.elastic.search(index=self.es_index, body=query_body)
        except NotFoundError:
            return None
        return [self.model(**doc['_source']) for doc in docs["hits"]["hits"]]

    def build_search_query(self, params: ModelParams) -> str | None:
        """Основная функция генерации json по модели тела запроса."""
        return self._build_query_body(params=params).json(by_alias=True, exclude_none=True)

    def _build_query_body(self, params: ModelParams):
        """Основная функция генерации модели тела запроса.
        Реализованна базовая востребованная для всех моделей логика:
            генерации параметров запроса - фильтр по ID.
        Для работы сортировки необходима реализация _build_query_order,
        которая должна возвращать поле для сортировки.
        """
        body = self._build_query_body_()
        query = self._build_query()
        body.query = query

        if params.ids:
            if not query.bool:
                query.bool = self._build_query_bool()

            values = [
                str(_id) for _id in params.ids
            ]
            ids_values = self._build_ids_values(values=values)
            query.bool.filter = self._build_query_ids(ids=ids_values)

        if params.sort:
            if params.sort.startswith('-'):
                order = es_query.OrderEnum.DESC
            else:
                order = es_query.OrderEnum.ASC
            body.sort = self._build_query_order(order=order)

        body.size = params.page_size
        body.from_ = params.page_num
        return body

    # Вспомогательные функции, для генерации моделей запроса.
    def _build_query_order(self, order: es_query.OrderEnum) -> Any:
        """Функция генерации модели, для поля сортировки."""
        pass

    def _build_ids_values(self, values: list[str]) -> es_query.IDSValues:
        return es_query.IDSValues(
            values=values
        )

    def _build_query_ids(self, ids: es_query.IDSValues) -> es_query.IDS:
        return es_query.IDS(
            ids=ids
        )

    def _build_query_body_(self) -> es_query.ESBodyQuery:
        return es_query.ESBodyQuery()

    def _build_query_match(
            self,
            query: str,
            match_field_type: Any,
            match_field_name: str,
    ) -> es_query.Match:
        match_field_query = es_query.MatchFieldQuery(
            query=query,
        )

        match_field = match_field_type(
            **{
                match_field_name: match_field_query
            }
        )

        return es_query.Match(
            match=match_field
        )

    def _build_query(self) -> es_query.Query:
        return es_query.Query()

    def _build_query_bool(self) -> es_query.QueryBool:
        return es_query.QueryBool()
    #
    def _build_query_term(
            self,
            term_field_type: Any,
            term_field_name: str,
            term_field_value: str,
    ) -> es_query.Term:
        term_field = term_field_type(
            **{
                term_field_name: term_field_value
            }
        )
        return es_query.Term(
            term=term_field
        )

    def _build_or_get_query_nested(
            self,
            path: str,
            body: es_query.ESBodyQuery,
    ) -> es_query.Nested:
        """Функция создания структуры nested поискового запроса ES."""
        nested = None
        if body and body.query and body.query.bool and\
           body.query.bool.must:
            for el in body.query.bool.must:
                if isinstance(el, es_query.Nested):
                    nested = el

        if not nested:
            query = self._build_query()
            query.bool = self._build_query_bool()

            nested_inner = es_query.NestedInner(
                path=path,
                query=query
            )
            nested = es_query.Nested(nested=nested_inner)
        return nested

    def _build_query_bool_must(
            self,
            body: es_query.ESBodyQuery
    ) -> es_query.ESBodyQuery:
        if not body.query.bool:
            body.query.bool = self._build_query_bool()
        if not body.query.bool.must:
            body.query.bool.must = []
        return body
