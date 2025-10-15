from datetime import date

from src.exceptions import ObjectNotFoundException, HotelNotFoundException, RoomNotFoundException
from src.schemas.facilities import RoomFacilityAdd
from src.schemas.rooms import Room, RoomAdd, RoomPATCH
from src.services.base import BaseService
from src.services.hotels import HotelService


class RoomService(BaseService):
    async def get_filtered_by_time(
            self,
            date_from: date,
            date_to: date,
            hotel_id: int,
    ):
        return await self.db.rooms.get_filtered_by_time(
            date_from=date_from, date_to=date_to, hotel_id=hotel_id
        )
    
    async def get_room(self, room_id: int):
        return await self.db.rooms.get_one_with_facilities(room_id)

    async def create_room(
            self,
            room_data: RoomAdd,
    ):
        room = await self.db.rooms.add(room_data)

        if room_data.facilities_ids:
            rooms_facilities_data = [
                RoomFacilityAdd(room_id=room.id, facility_id=f_id) for f_id in room_data.facilities_ids
            ]
            await self.db.rooms_facilities.add_bulk(rooms_facilities_data)

        await self.db.commit()

        return room

    async def edit_room(
            self,
            room_id: int,
            update_data: RoomAdd,
    ):
        await self.db.rooms.edit_with_facilities(update_data, id=room_id)
        await self.db.commit()

    async def partially_edit_room(
            self,
            room_id: int,
            room_data: RoomPATCH,
    ):
        await self.db.rooms.edit_with_facilities(room_data, is_patch=True, id=room_id)
        await self.db.commit()

    async def delete_room(self, hotel_id: int, room_id: int):
        await self.db.rooms.delete(id=room_id)

    async def get_room_with_check(self, room_id: int) -> Room:
        try:
            return await self.db.rooms.get_one(id=room_id)
        except ObjectNotFoundException:
            raise RoomNotFoundException