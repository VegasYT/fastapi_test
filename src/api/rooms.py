from datetime import date
from fastapi import Query, Body, APIRouter, HTTPException

from src.schemas.facilities import RoomFacilityAdd
from src.schemas.rooms import RoomAdd, RoomPATCH
from src.api.dependencies import DBDep


router = APIRouter(prefix="/rooms", tags=["Номера"])


@router.get("")
async def get_rooms(
    db: DBDep,
    # pagination: PaginationDep,
    # room_title: str | None = Query(None, description="Название номера"),
    hotel_id: int | None = Query(None, description="ID отеля"),
    date_from: date | None = Query(None, description="Дата заезда", examples=["2025-08-08"]),
    date_to: date | None = Query(None, description="Дата выезда", examples=["2025-08-10"]),
):
    # page_size = pagination.page_size or 5
    # limit = page_size
    # offset = page_size * (pagination.page_number - 1)

    return await db.rooms.get_filtered_by_time(
        date_from=date_from,
        date_to=date_to,
        # room_title=room_title,
        hotel_id=hotel_id,
        # limit=limit,
        # offset=offset
    )


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
    room = await db.rooms.add(room_data)

    rooms_facilities_data = [
        RoomFacilityAdd(room_id=room.id, facility_id=f_id) for f_id in room_data.facilities_ids
    ]
    await db.rooms_facilities.add_bulk(rooms_facilities_data)

    await db.commit()
    return {"status": "OK", "data": room}


@router.get("/{room_id}")
async def get_room(db: DBDep, room_id: int):
    room = await db.rooms.get_one_with_facilities(room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Номер не найден")
    return room


@router.put("/{room_id}")
async def edit_room(
    db: DBDep,
    room_id: int,
    update_data: RoomAdd = Body(),
):
    await db.rooms.edit_with_facilities(update_data, id=room_id)

    await db.commit()
    return {"status": "OK"}


@router.patch(
    "/{room_id}",
    summary="Частичное обновление данных номера",
    description="<h1>Тут мы частично обновляем данные номера</h1>",
)
async def partially_edit_room(db: DBDep, room_id: int, room_data: RoomPATCH):
    await db.rooms.edit_with_facilities(room_data, is_patch=True, id=room_id)

    await db.commit()
    return {"status": "OK"}


@router.delete("/{room_id}")
async def delete_room(db: DBDep, room_id: int):
    await db.rooms.delete(id=room_id)

    await db.commit()
    return {"status": "OK"}
