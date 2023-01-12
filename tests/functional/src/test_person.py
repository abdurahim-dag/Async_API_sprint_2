import pytest
import json
from functional.settings import genre_test_settings, test_settings
from functional.models import FilmDetail


@pytest.mark.parametrize('es_init', [genre_test_settings], indirect=True)
@pytest.mark.parametrize('random_line', [genre_test_settings.data_file_path], indirect=True)
@pytest.mark.asyncio
async def test_person_cache(es_init, es_client, random_line, redis_client, make_get_request):
    """Поиск конкретной персоны, с учётом кеша в Redis."""
    film_dict = json.loads(random_line)
    film = FilmDetail(**film_dict)

    url = test_settings.api_endpoint_films + str(film.id)
    response = await make_get_request(url)

    assert response.status == 200

    doc = {
        "doc": {'title': 'Unexpected'}
    }
    await es_client.update(index=genre_test_settings.index_name, id=film.id, body=doc)

    url = test_settings.api_endpoint_films + str(film.id)
    response = await make_get_request(url)

    assert response.status == 200
    assert response.headers.get("Cache-Control") is not None
    assert response.headers["Cache-Control"] is not None

    film_cache_response = FilmDetail(**response.json)

    url = test_settings.es_conn_str + '/'
    url += genre_test_settings.index_name + '/_doc/'
    url += str(film.id)

    response = await make_get_request(url)

    film_es_response = FilmDetail(**response.json['_source'])

    assert response.status == 200
    assert film.dict() == film_cache_response.dict()
    assert film_es_response.title == 'Unexpected'


@pytest.mark.parametrize('es_init', [genre_test_settings], indirect=True)
@pytest.mark.parametrize('random_line', [genre_test_settings.data_file_path], indirect=True)
@pytest.mark.asyncio
async def test_person_by_id(es_init, es_client, random_line, redis_client, make_get_request):
    """Поиск конкретной персоны."""
    # Выбираем рандомный фильм из исходных тестовых данных.
    film_dict = json.loads(random_line)
    film = FilmDetail(**film_dict)

    # Получаем выбранный фильм из api, по id.
    url = test_settings.api_endpoint_films + str(film.id)
    response = await make_get_request(url)
    film_api_response = FilmDetail(**response.json)

    assert response.status == 200
    assert film.dict() == film_api_response.dict()


@pytest.mark.parametrize('es_init', [genre_test_settings], indirect=True)
@pytest.mark.parametrize('random_line', [genre_test_settings.data_file_path], indirect=True)
@pytest.mark.asyncio
async def test_person_list(es_init, es_client, random_line, redis_client, make_get_request):
    """Вывод списка персон, с учётом кеша в Redis."""
    # Проверка на вывод 10 персон.
    page_num = 0
    page_size = 20
    params = {
        'page[number]': page_num,
        'page[size]': page_size,
    }
    url = test_settings.api_endpoint_films
    response = await make_get_request(url, params)

    assert response.status == 200
    assert len(response.json) == page_size


@pytest.mark.parametrize('es_init', [genre_test_settings], indirect=True)
@pytest.mark.parametrize('random_line', [genre_test_settings.data_file_path], indirect=True)
@pytest.mark.asyncio
async def test_person_exception(es_init, es_client, random_line, redis_client, make_get_request):
    """Тест пограничных состояний"""
    # Проверка на вывод 20 фильмов.

    sort = '-title'
    params = {
        'sort': sort,
    }
    url = test_settings.api_endpoint_films
    response = await make_get_request(url, params)

    assert response.status == 422
    assert response.json['detail'][0][
               'msg'] == "value is not a valid enumeration member; permitted: 'imdb_rating', '-imdb_rating'"

    filter_genre = 'incorrect uuid'
    params = {
        'filter[genre]': filter_genre,
    }
    url = test_settings.api_endpoint_films
    response = await make_get_request(url, params)

    assert response.status == 422
    assert response.json['detail'][0]['msg'] == 'value is not a valid uuid'