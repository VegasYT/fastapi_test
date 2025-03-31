from fastapi import Query, Body, APIRouter, Body
from sqlalchemy import insert, select, func

from repos.hotels import HotelsRepository
from src.schemas.hotels import Hotel, HotelPATCH
from src.api.dependencies import PaginationDep
from src.database import async_session_maker, engine
from src.models.hotels import HotelsOrm
 

router = APIRouter(prefix="/hotels", tags=["Отели"])
 

@router.get("/{hotel_id}")
async def get_hotel(hotel_id: int):
    async with async_session_maker() as session:
        return await HotelsRepository(session).get_one_or_none(
            id=hotel_id
        )

    
@router.get("")
async def get_hotels(
        pagination: PaginationDep,
        location: str | None = Query(None, description="Местоположение"),
        title: str | None = Query(None, description="Название отеля"),
):
    page_size = pagination.page_size or 5
    limit = page_size
    offset = page_size * (pagination.page_number - 1)
    
    async with async_session_maker() as session:
        return await HotelsRepository(session).get_all(
            location=location, 
            title=title, 
            limit=limit, 
            offset=offset
        )


@router.post("")
async def create_hotel(hotel_data: Hotel = Body(openapi_examples={
    "1": {
        "summary": "Сочи",
        "value": {
            "title": "SunResort",
            "location": "г. Сочи, ул.Ленина, д.12",
        }
    },
    "2": {
        "summary": "Дубай",
        "value": {
            "title": "RelaxHotel",
            "location": "г. Дубай, ул.Пушкина, д.24",
        }
    }
}),
):
    async with async_session_maker() as session:
        hotel = await HotelsRepository(session).add(hotel_data)
        await session.commit()

    return {"status": "OK", "data": hotel}


@router.put("/{hotel_id}")
async def edit_hotel(
        hotel_id: int,
        update_data: Hotel = Body(),
):
    async with async_session_maker() as session:
        await HotelsRepository(session).edit(
            update_data, 
            id=hotel_id
        )
        await session.commit()

    return {"status": "OK"}


@router.patch(
    "/{hotel_id}",
    summary="Частичное обновление данных об отеле",
    description="<h1>Тут мы частично обновляем данные об отеле: можно отправить name, а можно title</h1>",
)
async def partially_edit_hotel(
        hotel_id: int,
        hotel_data: HotelPATCH
):
    async with async_session_maker() as session:
        await HotelsRepository(session).edit(
            hotel_data, 
            is_patch=True, 
            id=hotel_id
        )
        await session.commit()

    return {"status": "OK"}


@router.delete("/{hotel_id}")
async def delete_hotel(hotel_id: int):
    async with async_session_maker() as session:
        await HotelsRepository(session).delete(
            id=hotel_id
        )
        await session.commit()

    return {"status": "OK"}
