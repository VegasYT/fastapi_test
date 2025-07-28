from fastapi import Query, Body, APIRouter, Body, HTTPException
from sqlalchemy import insert, select, func

from src.repos.hotels import HotelsRepository
from src.schemas.hotels import Hotel, HotelAdd, HotelPATCH
from src.api.dependencies import DBDep, PaginationDep
from src.database import async_session_maker, engine
from src.models.hotels import HotelsOrm
 

router = APIRouter(prefix="/hotels", tags=["Отели"])
 

@router.get("")
async def get_hotels(
    db: DBDep,
    pagination: PaginationDep,
    location: str | None = Query(None, description="Местоположение"),
    title: str | None = Query(None, description="Название отеля"),
):
    page_size = pagination.page_size or 5
    # limit = page_size
    offset = page_size * (pagination.page_number - 1)
    
    return await db.hotels.get_all(
        location=location, 
        title=title, 
        limit=page_size, 
        offset=offset
    )


@router.post("")
async def create_hotel(
    db: DBDep,
    hotel_data: HotelAdd = Body(openapi_examples={
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
    hotel = await db.hotels.add(hotel_data)

    return {"status": "OK", "data": hotel}


@router.get("/{hotel_id}")
async def get_hotel(
    db: DBDep,
    hotel_id: int
):
    hotel = await db.hotels.get_one_or_none(id=hotel_id)
    
    if hotel is None:
        raise HTTPException(status_code=404, detail="Отель не найден")
    
    return hotel


@router.put("/{hotel_id}")
async def edit_hotel(
    db: DBDep,
    hotel_id: int,
    update_data: HotelAdd = Body(),
):
    await db.hotels.edit(
        update_data, 
        id=hotel_id
    )

    return {"status": "OK"}


@router.patch(
    "/{hotel_id}",
    summary="Частичное обновление данных об отеле",
    description="<h1>Тут мы частично обновляем данные об отеле: можно отправить name, а можно title</h1>",
)
async def partially_edit_hotel(
    db: DBDep,
    hotel_id: int,
    hotel_data: HotelPATCH
):
    await db.hotels.edit(
        hotel_data, 
        is_patch=True, 
        id=hotel_id
    )

    return {"status": "OK"}


@router.delete("/{hotel_id}")
async def delete_hotel(
    db: DBDep,
    hotel_id: int
):
    await db.hotels.delete(
        id=hotel_id
    )

    return {"status": "OK"}