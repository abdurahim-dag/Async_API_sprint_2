"""Тест ручек API, для жанров."""
import pytest
import json
from functional.settings import genre_index, settings
from functional.models import Genre, GenreDetail

@pytest.mark.parametrize('random_line',[genre_index.data_file_path], indirect=True)
@pytest.mark.asyncio
async def test_genre_by_id(es_init, random_line, redis_client, make_get_request):
    """Тест поиска конкретного жанра."""
    # Выбираем рандомный жанр из исходных тестовых данных.
    genre_dict = json.loads(random_line)
    genre = GenreDetail(**genre_dict)

    # Получаем выбранный жанр из api, по id.
    url = settings.api_endpoint_genres + str(genre.id)
    response = await make_get_request(url)
    genre_api = GenreDetail(**response.json)

    assert response.status == 200
    assert genre.dict() == genre_api.dict()


@pytest.mark.parametrize('random_line',[genre_index.data_file_path], indirect=True)
@pytest.mark.asyncio
async def test_genre_cache(es_init, es_client, random_line, redis_client, make_get_request):
    """Тест поиска конкретного жанра, с учётом кеша в Redis."""
    # Выбираем рандомный жанр из исходных тестовых данных.
    genre_dict = json.loads(random_line)
    genre = GenreDetail(**genre_dict)

    # Получаем выбранный жанр из api, по id.
    url = settings.api_endpoint_genres + str(genre.id)
    response = await make_get_request(url)
    genre_api = GenreDetail(**response.json)

    assert response.status == 200
    assert genre.dict() == genre_api.dict()

    # Обновляем запись об этом жанре в ES.
    doc = {
        "doc": {'name': 'Unexpected'}
    }
    await es_client.update(index=genre_index.index_name, id=genre.id, body=doc)

    # Вновь забираем жанр из API, ожидая, что мы берём его из кэша.
    url = settings.api_endpoint_genres + str(genre.id)
    response = await make_get_request(url)
    genre_cached = GenreDetail(**response.json)

    assert response.status == 200
    assert response.headers.get("Cache-Control") is not None
    assert response.headers["Cache-Control"] is not None

    # Для проверки забираем измененный жанр напрямую из ES.
    url = f"{settings.es_conn_str}/{genre_index.index_name}/_doc/{str(genre.id)}"

    response = await make_get_request(url)
    genre_es = GenreDetail(**response.json['_source'])

    assert response.status == 200

    assert genre == genre_cached
    assert genre_es.name == 'Unexpected'


@pytest.mark.asyncio
async def test_genre_list(es_init, make_get_request):
    """Тест вывод списка N жанров."""
    url = settings.api_endpoint_genres
    response = await make_get_request(url)

    assert response.status == 200
    assert len(response.json) == 25


@pytest.mark.asyncio
async def test_genre_page_num_over(es_init, make_get_request):
    """Тест вывода списка N жанров, больше чем есть."""
    page_num = 1000
    page_size = 50
    params ={
        'page[number]': page_num,
        'page[size]': page_size,
    }
    url = settings.api_endpoint_genres
    response = await make_get_request(url, params)

    assert response.status == 404
    assert response.json['detail'] == 'genre not found'


@pytest.mark.asyncio
async def test_genre_page_size_minus(es_init, make_get_request):
    """Тест вывода списка N жанров, в отрицательную сторону."""
    page_num = 1
    page_size = -50
    params ={
        'page[number]': page_num,
        'page[size]': page_size,
    }
    url = settings.api_endpoint_genres
    response = await make_get_request(url, params)

    assert response.status == 422
    assert response.json['detail'][0]['loc'] == ['query', 'page[size]']
