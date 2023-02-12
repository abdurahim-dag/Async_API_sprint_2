"""Тест ручки API, для фильма."""
import json
from http import HTTPStatus

import pytest

from functional.models import FilmDetail
from functional.settings import film_index, settings


@pytest.mark.parametrize('es_init',[film_index], indirect=True)
@pytest.mark.parametrize('random_line',[film_index.data_file_path], indirect=True)
@pytest.mark.asyncio
async def test_film_by_id(es_init, random_line, make_get_request):
    """Тест поиска конкретного фильма."""
    # Выбираем рандомный фильм из исходных тестовых данных.
    film_dict = json.loads(random_line)
    film = FilmDetail(**film_dict)
    url = settings.api_endpoint_films + str(film.id)

    # Получаем выбранный фильм из api, по id.
    response = await make_get_request(url)
    film_api = FilmDetail(**response.json)

    assert response.status == HTTPStatus.OK
    assert film.dict() == film_api.dict()


@pytest.mark.parametrize('es_init',[film_index], indirect=True)
@pytest.mark.parametrize('random_line',[film_index.data_file_path], indirect=True)
@pytest.mark.asyncio
async def test_film_cache(es_init, es_client, random_line, make_get_request):
    """Тест поиска конкретного фильма, с учётом кеша в Redis."""
    # Выбираем рандомный фильм из исходных тестовых данных.
    film_dict = json.loads(random_line)
    film = FilmDetail(**film_dict)
    url = settings.api_endpoint_films + str(film.id)
    doc = {
        "doc": {'title': 'Unexpected'}
    }

    # Получаем выбранный фильм из api, по id.
    response = await make_get_request(url)

    assert response.status == HTTPStatus.OK

    # Обновляем запись об этом фильме в ES.
    await es_client.update(index=film_index.index_name, id=film.id, body=doc)

    # Вновь забираем фильм из API, ожидая, ято мы берём его из кэша.
    response = await make_get_request(url)

    assert response.status == HTTPStatus.OK
    assert response.headers.get("Cache-Control") is not None
    assert response.headers["Cache-Control"] is not None

    film_cache_response = FilmDetail(**response.json)
    # Для проверки забираем измененный фильм напрямую из ES.
    url = settings.es_conn_str + '/'
    url += film_index.index_name + '/_doc/'
    url += str(film.id)

    response = await make_get_request(url)
    film_api = FilmDetail(**response.json['_source'])

    assert response.status == HTTPStatus.OK
    assert film.dict() == film_cache_response.dict()
    assert film_api.title == 'Unexpected'


@pytest.mark.parametrize('es_init',[film_index], indirect=True)
@pytest.mark.parametrize('random_line',[film_index.data_file_path], indirect=True)
@pytest.mark.asyncio
async def test_film_list(es_init, random_line, make_get_request):
    """Тест вывод списка N фильмов."""
    # Проверка на вывод 20 фильмов.
    page_num = 0
    page_size = 20
    params ={
        'page[number]': page_num,
        'page[size]': page_size,
    }
    url = settings.api_endpoint_films

    response = await make_get_request(url, params)

    assert response.status == HTTPStatus.OK
    assert len(response.json) == page_size


@pytest.mark.parametrize('es_init',[film_index], indirect=True)
@pytest.mark.parametrize('random_line',[film_index.data_file_path], indirect=True)
@pytest.mark.asyncio
async def test_film_page_num_over(es_init, random_line, make_get_request):
    """Тест вывода списка N фильмов, больше чем есть."""
    page_num = 1000
    page_size = 50
    params ={
        'page[number]': page_num,
        'page[size]': page_size,
    }
    url = settings.api_endpoint_films

    response = await make_get_request(url, params)

    assert response.status == HTTPStatus.NOT_FOUND
    assert response.json['detail'] == 'films not found'


@pytest.mark.parametrize('es_init',[film_index], indirect=True)
@pytest.mark.parametrize('random_line',[film_index.data_file_path], indirect=True)
@pytest.mark.asyncio
async def test_film_page_size_minus(es_init, random_line, make_get_request):
    """Тест вывода списка N фильмов, в отрицательную сторону."""
    page_num = 1
    page_size = -50
    params ={
        'page[number]': page_num,
        'page[size]': page_size,
    }
    url = settings.api_endpoint_films

    response = await make_get_request(url, params)

    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json['detail'][0]['loc'] == ['query', 'page[size]']


@pytest.mark.parametrize('es_init', [film_index], indirect=True)
@pytest.mark.parametrize('random_line', [film_index.data_file_path], indirect=True)
@pytest.mark.asyncio
async def test_film_sort_param_422(es_init, random_line, make_get_request):
    """Проверка на exception, по не сортируемой параметру."""
    sort = '-title'
    params = {
        'sort': sort,
    }
    url = settings.api_endpoint_films

    response = await make_get_request(url, params)

    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json['detail'][0]['msg'] == "value is not a valid enumeration member; permitted: 'imdb_rating', '-imdb_rating'"

    filter_genre = 'incorrect uuid'
    params = {
        'filter[genre]': filter_genre,
    }

    response = await make_get_request(url, params)

    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json['detail'][0]['msg'] == 'value is not a valid uuid'
