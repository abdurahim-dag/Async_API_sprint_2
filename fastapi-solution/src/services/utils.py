import logging
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
            logging.info(search_query)
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

        if params.ids:
            query = body.query
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

        body.size = params.page_size
        body.from_ = params.page_num
        return body
