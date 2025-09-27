from datetime import date

from src.exceptions import HotelNotFoundException, ObjectNotFoundException
from src.schemas.hotels import Hotel, HotelAdd, HotelPATCH
from src.api.dependencies import PaginationDep
from src.services.base import BaseService


class HotelService(BaseService):
    async def get_filtered_by_time(
            self,
            location: str | None,
            title: str | None,
            date_from: date,
            date_to: date,
            pagination: PaginationDep,
    ):
        page_size = pagination.page_size or 5
        offset = page_size * (pagination.page_number - 1)

        hotels = await self.db.hotels.get_filtered_by_time(
            location=location,
            title=title,
            limit=page_size,
            offset=offset,
            date_from=date_from,
            date_to=date_to,
        )

        return hotels
    
    async def get_hotel(self, hotel_id: int):
        return await self.db.hotels.get_one(id=hotel_id)

    async def add_hotel(self, data: HotelAdd):
        hotel = await self.db.hotels.add(data)
        await self.db.commit()
        return hotel

    async def edit_hotel(self, hotel_id: int, data: HotelAdd):
        await self.db.hotels.edit(data, id=hotel_id)
        await self.db.commit()

    async def edit_hotel_partially(self, hotel_id: int, hotel_data: HotelPATCH, is_patch: bool = False):
        await self.db.hotels.edit(hotel_data, is_patch=is_patch, id=hotel_id)
        await self.db.commit()

    async def delete_hotel(self, hotel_id: int):
        await self.db.hotels.delete(id=hotel_id)
        await self.db.commit()