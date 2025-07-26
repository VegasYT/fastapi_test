from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from src.models.rooms import RoomsOrm
from src.models.hotels import HotelsOrm
from src.repos.base import BaseRepository
from src.schemas.rooms import Room


class RoomsRepository(BaseRepository):
    model = RoomsOrm
    schema = Room

    async def get_all(
        self, 
        room_title: str | None = None,
        hotel_title: str | None = None,
        hotel_id: int | None = None,
    ) -> list[Room]:
        query = select(RoomsOrm)
        
        if room_title:
            query = query.filter(
                func.lower(RoomsOrm.title).contains(room_title.strip().lower())
            )
        
        if hotel_title:
            query = query.join(HotelsOrm).filter(
                func.lower(HotelsOrm.title).contains(hotel_title.strip().lower())
            )

        if hotel_id:
            query = query.filter(RoomsOrm.hotel_id == hotel_id)

        result = await self.session.execute(query)
        return [Room.model_validate(room, from_attributes=True) for room in result.scalars().all()]