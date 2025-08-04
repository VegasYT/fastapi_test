from datetime import date
from sqlalchemy import func, select

from src.models.rooms import RoomsOrm
from src.repos.utils import rooms_ids_for_booking
from src.schemas.facilities import Facility
from src.models.facilities import FacilitiesOrm
from src.repos.base import BaseRepository


class FacilitiesRepository(BaseRepository):
    model = FacilitiesOrm
    schema = Facility

    async def get_filtered_by_pagination(
            self,
            limit: int | None = None,
            offset: int | None = None,
    ):
        query = select(FacilitiesOrm)

        # Пагинация
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)

        result = await self.session.execute(query)

        return [Facility.model_validate(facility, from_attributes=True) for facility in result.scalars().all()]