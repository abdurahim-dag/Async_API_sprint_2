"""Тест ручки API, для фильма."""
import logging

import pytest
import json
from functional.settings import film_index, settings
from functional.models import Film

@pytest.mark.parametrize('es_init',[film_index], indirect=True)
@pytest.mark.parametrize('random_line',[film_index.data_file_path], indirect=True)
@pytest.mark.asyncio
async def test_search_film_by_title(es_init, random_line, make_get_request):
    """Тест поиска записи по фразе и N записей."""
    # Выбираем рандомный фильм из исходных тестовых данных.
    film_dict = json.loads(random_line)
    film = Film(**film_dict)

    page_num = 1
    page_size = 10
    params ={
        'page[number]': page_num,
        'page[size]': page_size,
        'query': film.title,
    }

    url = settings.api_endpoint_films + 'search'
    response = await make_get_request(url, params=params)
    len_resp = len(response.json)

    assert response.status == 200
    assert len_resp == page_size or len_resp > 0


@pytest.mark.parametrize('es_init',[film_index], indirect=True)
@pytest.mark.parametrize('random_line',[film_index.data_file_path], indirect=True)
@pytest.mark.asyncio
async def test_cached_search_film_(es_init, es_client, random_line, make_get_request):
    """Тест поиска записи с учётом кеша в Redis."""
    # Выбираем рандомный фильм из исходных тестовых данных.
    film_dict = json.loads(random_line)
    film = Film(**film_dict)

    # Получаем список фильмов из API
    params ={
        'query': film.title,
    }
    url = settings.api_endpoint_films + 'search'

    response = await make_get_request(url, params=params)

    assert response.status == 200
    assert len(response.json) > 0

    # Выбираем первый
    film_api_first = Film(**response.json[0])

    # Обновляем запись об этом фильме в ES.
    doc = {
        "doc": {'title': 'Unexpected'}
    }
    await es_client.update(index=film_index.index_name, id=film.id, body=doc)

    # Вновь забираем фильм из API, ожидая, что мы берём его из кэша.
    response = await make_get_request(url, params=params)
    film_api_second = Film(**response.json[0])

    # Сравниваем результат с предыдущим
    assert film_api_first.dict() == film_api_second.dict()



