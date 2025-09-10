from datetime import date
from pydantic import BaseModel
from sqlalchemy import delete, insert, select
from sqlalchemy.orm import joinedload

from src.repos.mappers.mappers import RoomDataMapper, RoomDataWithRelsMapper
from src.models.facilities import RoomsFacilitiesOrm
from src.repos.utils import rooms_ids_for_booking
from src.models.rooms import RoomsOrm
from src.repos.base import BaseRepository
from src.schemas.rooms import Room, RoomWithRels


class RoomsRepository(BaseRepository):
    model = RoomsOrm
    mapper = RoomDataMapper

    async def get_filtered_by_time(
        self, 
        hotel_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ):
        rooms_ids_to_get = rooms_ids_for_booking(date_from, date_to, hotel_id)

        query = (
            select(self.model)
            .options(joinedload(self.model.facilities))
            .filter(RoomsOrm.id.in_(rooms_ids_to_get))
        )
        result = await self.session.execute(query)

        return [RoomDataWithRelsMapper.map_to_domain_entity(obj) for obj in result.unique().scalars().all()]


    async def get_room_price(
        self, 
        room_id
    ) -> int:
        query = select(RoomsOrm.price).where(RoomsOrm.id == room_id)

        result = await self.session.execute(query)

        return result.scalar_one()


    async def update_room_facilities(self, room_id: int, new_facility_ids: list[int] | None):
        """
        Обновляет удобства номера, выполняя минимум операций с БД.
        Удаляет только те связи, которые нужно удалить.
        Добавляет только те связи, которые нужно добавить.
        """
        if new_facility_ids is None:
            return
        
        # Получаем текущие facility_ids для данного номера
        current_facilities_query = (
            select(RoomsFacilitiesOrm.facility_id)
            .where(RoomsFacilitiesOrm.room_id == room_id)
        )
        result = await self.session.execute(current_facilities_query)
        current_facility_ids = set(result.scalars().all())
        
        new_facility_ids_set = set(new_facility_ids)
        
        # Определяем что нужно удалить и что нужно добавить
        facilities_to_delete = current_facility_ids - new_facility_ids_set
        facilities_to_add = new_facility_ids_set - current_facility_ids
        
        # Удаляем ненужные связи
        if facilities_to_delete:
            delete_stmt = (
                delete(RoomsFacilitiesOrm)
                .where(
                    RoomsFacilitiesOrm.room_id == room_id,
                    RoomsFacilitiesOrm.facility_id.in_(facilities_to_delete)
                )
            )
            await self.session.execute(delete_stmt)
        
        # Добавляем новые связи
        if facilities_to_add:
            insert_data = [
                {"room_id": room_id, "facility_id": facility_id}
                for facility_id in facilities_to_add
            ]
            insert_stmt = insert(RoomsFacilitiesOrm).values(insert_data)
            await self.session.execute(insert_stmt)


    async def edit_with_facilities(self, update_data: BaseModel, is_patch: bool = False, **filters_by):
        """
        Обновляет номер и его удобства, используя разные методы для разных частей
        """
        # Извлекаем facilities_ids из данных обновления
        update_dict = update_data.model_dump(exclude_unset=is_patch)
        facilities_ids = update_dict.pop('facilities_ids', None)
        
        # Если есть поля для обновления основной таблицы - используем базовый edit
        if update_dict:
            # Создаем новый объект без facilities_ids для базового edit
            update_data_without_facilities = update_data.__class__.model_validate(update_dict)
            await self.edit(update_data_without_facilities, is_patch=is_patch, **filters_by)
        
        # Обновляем facilities отдельным методом если они переданы
        if facilities_ids is not None or not is_patch:
            # Получаем room_id из filters_by (предполагаем что передается id=room_id)
            room_id = filters_by.get('id')
            if room_id:
                await self.update_room_facilities(room_id, facilities_ids)


    async def get_one_with_facilities(self, room_id: int):
        """Получить номер с загруженными facilities"""
        query = (
            select(self.model)
            .options(joinedload(self.model.facilities))
            .filter_by(id=room_id)
        )
        result = await self.session.execute(query)
        obj = result.unique().scalars().one_or_none()
        
        if obj is None:
            return None
        
        return RoomDataWithRelsMapper.map_to_domain_entity(obj)
