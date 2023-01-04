from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query

from models import Genre
from models import GenreDetail
from models.messages import Genre as Message
from services import GenreService
from services import cache
from services import get_genre_service


router = APIRouter()


@router.get(
    '',
    response_model=list[Genre],
    summary='Главная страница жанров.',
    description='На ней выводится полный список жанров.',
    response_description='Список жанров.',
)
@cache()
async def genre_list(
        genre_service: GenreService = Depends(get_genre_service),
        message: Message = Depends()
) -> list[Genre]:
    genres = await genre_service.get_list()
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=message.not_found)
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
        genre_service: GenreService = Depends(get_genre_service),
        message: Message = Depends()
) -> GenreDetail:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=message.not_found)
    return genre


