from datetime import date
from fastapi import Query, Body, APIRouter, HTTPException

from src.services.rooms import RoomService
from src.exceptions import IncorrectDateException, ObjectNotFoundException
from src.schemas.rooms import RoomAdd, RoomPATCH
from src.api.dependencies import DBDep


router = APIRouter(prefix="/rooms", tags=["Номера"])


@router.get("")
async def get_rooms(
    db: DBDep,
    hotel_id: int | None = Query(None, description="ID отеля"),
    date_from: date | None = Query(None, description="Дата заезда", example="2025-08-08"),
    date_to: date | None = Query(None, description="Дата выезда", example="2025-08-09"),
):
    try:
        rooms = await RoomService(db).get_filtered_by_time(date_from, date_to, hotel_id)
    except IncorrectDateException as ex:
        raise HTTPException(status_code=400, detail=ex.detail)
    
    return rooms
    

@router.post("")
async def create_room(
    db: DBDep,
    room_data: RoomAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Эконом",
                "value": {
                    "hotel_id": 1,
                    "title": "Эконом трехместный",
                    "description": "Большая двухместная кровать + одноместная",
                    "price": 1000,
                    "quantity": 5,
                    "facilities_ids": [1],
                },
            },
            "2": {
                "summary": "Люкс",
                "value": {
                    "hotel_id": 1,
                    "title": "Люкс двухместный",
                    "description": "Большая двухместная кровать",
                    "price": 5000,
                    "quantity": 2,
                    "facilities_ids": [1, 2],
                },
            },
        }
    ),
):
    try:
        room = await RoomService(db).create_room(room_data)
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail="Отель не найден")

    return {"status": "OK", "data": room}


@router.get("/{room_id}")
async def get_room(db: DBDep, room_id: int):
    try:
        room = await RoomService(db).get_room(room_id)
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail="Номер не найден")
    return room


@router.put("/{room_id}")
async def edit_room(
    db: DBDep,
    room_id: int,
    update_data: RoomAdd = Body(),
):
    try:
        await RoomService(db).edit_room(room_id, update_data)
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail="Обьект не найден")

    return {"status": "OK"}


@router.patch(
    "/{room_id}",
    summary="Частичное обновление данных номера",
    description="<h1>Тут мы частично обновляем данные номера</h1>",
)
async def partially_edit_room(db: DBDep, room_id: int, room_data: RoomPATCH):
    try:
        await RoomService(db).partially_edit_room(room_id, room_data)
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail="Обьект не найден")

    return {"status": "OK"}


@router.delete("/{room_id}")
async def delete_room(db: DBDep, room_id: int):
    try:
        await RoomService(db).delete_room(room_id)
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail="Обьект не найден")

    await db.commit()
    return {"status": "OK"}
