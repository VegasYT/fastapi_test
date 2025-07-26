from fastapi import Query, Body, APIRouter, Body, HTTPException

from src.repos.rooms import RoomsRepository
from src.schemas.rooms import Room, RoomAdd, RoomPATCH
from src.database import async_session_maker, engine
 

router = APIRouter(prefix="/rooms", tags=["Номера"])
 

@router.get("")
async def get_rooms(
    room_title: str | None = Query(None, description="Название номера"),
    hotel_title: str | None = Query(None, description="Название отеля"),
    hotel_id: int | None = Query(None, description="ID отеля"),
):
    async with async_session_maker() as session:
        return await RoomsRepository(session).get_all(
            room_title=room_title,
            hotel_title=hotel_title,
            hotel_id=hotel_id,
        )


@router.post("")
async def create_room(room_data: RoomAdd = Body(openapi_examples={
    "1": {
        "summary": "Эконом",
        "value": {
            "hotel_id": 1,
            "title": "Эконом трехместный",
            "description": "Большая двухместная кровать + одноместная",
            "price": 1000,
            "quantity": 5,
        }
    },
    "2": {
        "summary": "Люкс",
        "value": {
            "hotel_id": 1,
            "title": "Люкс двухместный",
            "description": "Большая двухместная кровать",
            "price": 5000,
            "quantity": 2,
        }
    }
}),
):
    async with async_session_maker() as session:
        room = await RoomsRepository(session).add(room_data)
        await session.commit()

    return {"status": "OK", "data": room}


@router.get("/{room_id}")
async def get_room(
    room_id: int
):
    async with async_session_maker() as session:
        room = await RoomsRepository(session).get_one_or_none(id=room_id)
        if room is None:
            raise HTTPException(status_code=404, detail="Номер не найден")
@router.put("/{room_id}")
async def edit_create_room(
        room_id: int,
        update_data: RoomAdd = Body(),
):
    async with async_session_maker() as session:
        await RoomsRepository(session).edit(
            update_data, 
            id=room_id
        )
        await session.commit()

    return {"status": "OK"}


@router.patch(
    "/{room_id}",
    summary="Частичное обновление данных номера",
    description="<h1>Тут мы частично обновляем данные номера</h1>",
)
async def partially_edit_room(
        room_id: int,
        room_data: RoomPATCH
):
    async with async_session_maker() as session:
        await RoomsRepository(session).edit(
            room_data, 
            is_patch=True, 
            id=room_id
        )
        await session.commit()

    return {"status": "OK"}


@router.delete("/{room_id}")
async def delete_room(room_id: int):
    async with async_session_maker() as session:
        await RoomsRepository(session).delete(
            id=room_id
        )
        await session.commit()

    return {"status": "OK"}