from sqlalchemy import select

from src.repos.mappers.mappers import FacilityDataMapper, RoomFacilityDataMapper
from src.schemas.facilities import Facility
from src.models.facilities import FacilitiesOrm, RoomsFacilitiesOrm
from src.repos.base import BaseRepository


class FacilitiesRepository(BaseRepository):
    model = FacilitiesOrm
    mapper = FacilityDataMapper

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

        return [
            Facility.model_validate(facility, from_attributes=True)
            for facility in result.scalars().all()
        ]


class RoomsFacilitiesRepository(BaseRepository):
    model = RoomsFacilitiesOrm
    mapper = RoomFacilityDataMapper
