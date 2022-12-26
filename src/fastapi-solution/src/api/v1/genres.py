from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from models import Genre, GenreDetail
from services import cache, GenreService, get_genre_service

router = APIRouter()


@router.get(
    '',
    response_model=list[Genre],
    summary='Главная страница жанров.',
    description='На ней выводится полный список жанров.',
    response_description='Список жанров.',
)
@cache()
async def genre_list(genre_service: GenreService = Depends(get_genre_service)) -> list[Genre]:
    genres = await genre_service.get_list()
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    return genres


@router.get(
    '/{genre_id}',
    response_model=GenreDetail,
    summary='Информация о жанре.',
    description='Детальная информация о жанре.',
    response_description='Жанр со всеми полями.',
)
@cache()
async def genre_detail(
        genre_id: UUID = Query(None, description='ID жанра.'),
        genre_service: GenreService = Depends(get_genre_service)
) -> GenreDetail:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    return genre


