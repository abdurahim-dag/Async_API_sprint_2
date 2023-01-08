"""Тест ручки API, для фильма."""
import pytest
import json
from functional.settings import film_test_settings, test_settings
from functional.models import FilmDetail

@pytest.mark.parametrize('es_init',[film_test_settings], indirect=True)
@pytest.mark.parametrize('random_line',[film_test_settings.data_file_path], indirect=True)
@pytest.mark.asyncio
async def test_film_by_id(es_init, es_client, random_line, redis_client, make_get_request):
    """Поиск конкретного фильма, с учётом кеша в Redis."""
    # Выбираем рандомный фильм из исходных тестовых данных.
    film_dict = json.loads(random_line)
    film = FilmDetail(**film_dict)

    # Получаем выбранный фильм из api, по id.
    url = test_settings.api_endpoint_films + str(film.id)
    response = await make_get_request(url)

    assert response.status == 200

    film_api_response = FilmDetail(**response.json)

    # Обновляем запись об этом фильме в ES.
    doc = {
        "doc": {'title': 'Unexpected'}
    }
    await es_client.update(index=film_test_settings.index_name, id=film.id, body=doc)

    # Вновь забираем фильм из API, ожидая, ято мы берём его из кэша.
    url = test_settings.api_endpoint_films + str(film.id)
    response = await make_get_request(url)

    assert response.status == 200
    assert response.headers.get("Cache-Control") is not None
    assert response.headers["Cache-Control"] is not None

    film_cache_response = FilmDetail(**response.json)

    # Для проверки забираем измененный фильм напрямую из ES.
    url = test_settings.es_conn_str + '/'
    url += film_test_settings.index_name + '/_doc/'
    url += str(film.id)

    response = await make_get_request(url)

    assert response.status == 200

    film_es_response = FilmDetail(**response.json['_source'])

    assert film.dict() == film_api_response.dict()
    assert film.dict() == film_cache_response.dict()
    assert film_es_response.title == 'Unexpected'


@pytest.mark.parametrize('es_init',[film_test_settings], indirect=True)
@pytest.mark.parametrize('random_line',[film_test_settings.data_file_path], indirect=True)
@pytest.mark.asyncio
async def test_film_list(es_init, es_client, random_line, redis_client, make_get_request):
    """Вывод списка фильмов, с учётом кеша в Redis."""
    # Выведем 20 фильмов.
    page_num = 0
    page_size = 20
    params ={
        'page[number]': page_num,
        'page[size]': page_size,
    }
    url = test_settings.api_endpoint_films
    response = await make_get_request(url, params)
    print("response")
    print(response)
    len = len(response)

    # sort
    #
    # filter_genre
    #
    # filter_genre_name
    #
    # film_dict = json.loads(random_line)
    # film = FilmDetail(**film_dict)
    #
    #
    # assert response.status == 200
    #
    # film_api_response = FilmDetail(**response.json)
    #
    # # Обновляем запись об этом фильме в ES.
    # doc = {
    #     "doc": {'title': 'Unexpected'}
    # }
    # await es_client.update(index=film_test_settings.index_name, id=film.id, body=doc)
    #
    # # Вновь забираем фильм из API, ожидая, ято мы берём его из кэша.
    # url = test_settings.api_endpoint_films + str(film.id)
    # response = await make_get_request(url)
    #
    # assert response.status == 200
    # assert response.headers.get("Cache-Control") is not None
    # assert response.headers["Cache-Control"] is not None
    #
    # film_cache_response = FilmDetail(**response.json)
    #
    # # Для проверки забираем измененный фильм напрямую из ES.
    # url = test_settings.es_conn_str + '/'
    # url += film_test_settings.index_name + '/_doc/'
    # url += str(film.id)
    #
    # response = await make_get_request(url)
    #
    # assert response.status == 200
    #
    # film_es_response = FilmDetail(**response.json['_source'])
    #
    # assert film.dict() == film_api_response.dict()
    # assert film.dict() == film_cache_response.dict()
    # assert film_es_response.title == 'Unexpected'
    #
    #
