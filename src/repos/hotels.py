from sqlalchemy import func, select
from schemas.hotels import Hotel
from src.models.hotels import HotelsOrm
from repos.base import BaseRepository


class HotelsRepository(BaseRepository):
    model = HotelsOrm
    shema = Hotel

    async def get_all(
            self, 
            location,
            title,
            limit,
            offset,
        ) -> list[Hotel]:
        query = select(HotelsOrm)
        if location:
            query = query.filter(func.lower(HotelsOrm.location).contains(location.strip().lower()))
        if title:
            query = query.filter(func.lower(HotelsOrm.title).contains(title.strip().lower()))
        query = (
            query
            .limit(limit)
            .offset(offset)
        )

        # print(query.compile(engine, compile_kwargs={"literal_binds": True})) 
        result = await self.session.execute(query)

        return [Hotel.model_validate(hotel, from_attributes=True) for hotel in result.scalars().all()]
