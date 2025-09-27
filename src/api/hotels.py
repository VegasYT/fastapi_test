from datetime import date
from fastapi import Query, Body, APIRouter, HTTPException

from src.services.hotels import HotelService
from src.exceptions import IncorrectDateException, ObjectNotFoundException
from src.schemas.hotels import HotelAdd, HotelPATCH
from src.api.dependencies import DBDep, PaginationDep


router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("")
async def get_hotels(
    db: DBDep,
    pagination: PaginationDep,
    location: str | None = Query(None, description="Местоположение"),
    title: str | None = Query(None, description="Название отеля"),
    date_from: date = Query(examples=["2025-07-02"]),
    date_to: date = Query(examples=["2025-07-11"]),
):
    try:
        hotels = await HotelService(db).get_filtered_by_time(
            location,
            title,
            date_from,
            date_to,
            pagination,
        )
    except IncorrectDateException as ex:
        raise HTTPException(status_code=400, detail=ex.detail)

    return hotels


@router.post("")
async def create_hotel(
    db: DBDep,
    hotel_data: HotelAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Сочи",
                "value": {
                    "title": "SunResort",
                    "location": "г. Сочи, ул.Ленина, д.12",
                },
            },
            "2": {
                "summary": "Дубай",
                "value": {
                    "title": "RelaxHotel",
                    "location": "г. Дубай, ул.Пушкина, д.24",
                },
            },
        }
    ),
):
    hotel = await HotelService(db).add_hotel(hotel_data)

    return {"status": "OK", "data": hotel}


@router.get("/{hotel_id}")
async def get_hotel(db: DBDep, hotel_id: int):
    try:
        hotel = await HotelService(db).get_hotel(hotel_id)
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail="Отель не найден")

    return hotel


@router.put("/{hotel_id}")
async def edit_hotel(
    db: DBDep,
    hotel_id: int,
    update_data: HotelAdd = Body(),
):
    await HotelService(db).edit_hotel(hotel_id, update_data)

    await db.commit()
    return {"status": "OK"}


@router.patch(
    "/{hotel_id}",
    summary="Частичное обновление данных об отеле",
    description="<h1>Тут мы частично обновляем данные об отеле: можно отправить name, а можно title</h1>",
)
async def partially_edit_hotel(db: DBDep, hotel_id: int, hotel_data: HotelPATCH):
    await HotelService(db).edit_hotel_partially(hotel_id, hotel_data, is_patch=True)

    await db.commit()
    return {"status": "OK"}


@router.delete("/{hotel_id}")
async def delete_hotel(db: DBDep, hotel_id: int):
    await HotelService(db).delete_hotel(hotel_id)

    await db.commit()
    return {"status": "OK"}
