from datetime import date
from sqlalchemy import func, select

from src.models.rooms import RoomsOrm
from src.repos.utils import rooms_ids_for_booking
from src.schemas.hotels import Hotel
from src.models.hotels import HotelsOrm
from src.repos.base import BaseRepository


class HotelsRepository(BaseRepository):
    model = HotelsOrm
    schema = Hotel

    async def get_filtered_by_time(
            self,
            date_from: date,
            date_to: date,
            location: str | None = None,
            title: str | None = None,
            limit: int | None = None,
            offset: int | None = None,
    ):
        rooms_ids_to_get = rooms_ids_for_booking(date_from=date_from, date_to=date_to)
        hotels_ids_to_get = (
            select(RoomsOrm.hotel_id)
            .select_from(RoomsOrm)
            .filter(RoomsOrm.id.in_(rooms_ids_to_get))
        )

        # Основной запрос с фильтрами
        query = select(HotelsOrm).filter(HotelsOrm.id.in_(hotels_ids_to_get))

        if location:
            query = query.filter(
                func.lower(HotelsOrm.location).contains(location.strip().lower())
            )

        if title:
            query = query.filter(
                func.lower(HotelsOrm.title).contains(title.strip().lower())
            )

        # Пагинация
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)

        result = await self.session.execute(query)

        return [Hotel.model_validate(hotel, from_attributes=True) for hotel in result.scalars().all()]
        # return await self.get_filtered(HotelsOrm.id.in_(hotels_ids_to_get))