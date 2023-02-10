"""Тест ручки API, для персон."""
import pytest
import json
from functional.settings import person_index, settings
from functional.models import Person, PersonDetail, Film

@pytest.mark.parametrize('random_line',[person_index.data_file_path], indirect=True)
@pytest.mark.asyncio
async def test_person_by_id(es_init, random_line, make_get_request):
    """Тест поиска конкретной персоны."""
    # Выбираем рандомную персону из исходных тестовых данных.
    person_dict = json.loads(random_line)
    person = PersonDetail(**person_dict)

    # Получаем выбранный фильм из api, по id.
    url = settings.api_endpoint_persons + str(person.id)
    response = await make_get_request(url)
    person_api = PersonDetail(**response.json)

    assert response.status == 200
    assert person_api.dict() == person.dict()


@pytest.mark.parametrize('random_line',[person_index.data_file_path], indirect=True)
@pytest.mark.asyncio
async def test_person_cache(es_init, es_client, random_line, make_get_request):
    """Тест поиска конкретной персоны, с учётом кеша в Redis."""
    # Выбираем рандомную персону из исходных тестовых данных.
    person_dict = json.loads(random_line)
    person = PersonDetail(**person_dict)

    # Получаем выбранную персону из api, по id.
    url = settings.api_endpoint_persons + str(person.id)
    response = await make_get_request(url)
    person_api = PersonDetail(**response.json)

    assert response.status == 200
    assert person.dict() == person_api.dict()

    # Обновляем запись об этой персоне в ES.
    doc = {
        "doc": {'full_name': 'Unexpected'}
    }
    await es_client.update(index=person_index.index_name, id=person.id, body=doc)

    # Вновь забираем персону из API, ожидая, ято мы берём его из кэша.
    url = settings.api_endpoint_persons + str(person.id)
    response = await make_get_request(url)
    person_cached = PersonDetail(**response.json)

    assert response.status == 200
    assert response.headers.get("Cache-Control") is not None
    assert response.headers["Cache-Control"] is not None

    # Для проверки забираем измененную персону напрямую из ES.
    url = settings.es_conn_str + '/'
    url += person_index.index_name + '/_doc/'
    url += str(person.id)

    response = await make_get_request(url)
    person_api = PersonDetail(**response.json['_source'])

    assert response.status == 200
    assert person.dict() == person_cached.dict()
    assert person.dict() != person_api.dict()
    assert person_api.name == 'Unexpected'


@pytest.mark.asyncio
async def test_person_list(es_init, make_get_request):
    """Тест вывод списка N персон."""
    # Проверка на вывод 20 персон.
    page_num = 0
    page_size = 20
    params ={
        'page[number]': page_num,
        'page[size]': page_size,
    }
    url = settings.api_endpoint_persons + 'search'
    response = await make_get_request(url, params)

    assert response.status == 200
    assert len(response.json) == page_size

@pytest.mark.asyncio
async def test_film_page_size_minus(es_init, make_get_request):
    """Тест вывода списка N персон, в отрицательную сторону."""
    page_num = 1
    page_size = -50
    params ={
        'page[number]': page_num,
        'page[size]': page_size,
    }
    url = settings.api_endpoint_persons + 'search'
    response = await make_get_request(url, params)

    assert response.status == 422
    assert response.json['detail'][0]['loc'] == ['query', 'page[size]']


@pytest.mark.asyncio
async def test_person_sort_param_422(es_init, make_get_request):
    """Проверка на exception, по не сортируемой параметру."""
    sort = '-title'
    params = {
        'sort': sort,
    }
    url = settings.api_endpoint_persons + 'search'
    response = await make_get_request(url, params)

    assert response.status == 422
    assert "value is not a valid" in response.json['detail'][0]['msg']


@pytest.mark.parametrize('random_line',[person_index.data_file_path], indirect=True)
@pytest.mark.asyncio
async def test_person_film(es_init, es_client, random_line, make_get_request):
    """Тест поиска конкретной персоны."""
    # Выбираем рандомную персону из исходных тестовых данных.
    person_dict = json.loads(random_line)
    person = PersonDetail(**person_dict)

    p = await es_client.indices.get('*')
    # Получаем выбранную персону из api, по id.
    url = settings.api_endpoint_persons + f"{str(person.id)}/film"
    response = await make_get_request(url)

    assert response.status == 200
    assert len(response.json) > 0
