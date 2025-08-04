from datetime import date
from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update

from src.models.facilities import RoomsFacilitiesOrm
from src.repos.utils import rooms_ids_for_booking
from src.models.rooms import RoomsOrm
from src.repos.base import BaseRepository
from src.schemas.rooms import Room
# from src.database import engine


class RoomsRepository(BaseRepository):
    model = RoomsOrm
    schema = Room

    async def get_filtered_by_time(
        self, 
        hotel_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ):
        rooms_ids_to_get = rooms_ids_for_booking(date_from, date_to, hotel_id)

        return await self.get_filtered(RoomsOrm.id.in_(rooms_ids_to_get))


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
        Расширенная версия edit, которая также обрабатывает facilities_ids
        """
        # Проверяем валидность объекта
        await self._validate_single_object(**filters_by)
        
        # Извлекаем facilities_ids из данных обновления
        update_dict = update_data.model_dump(exclude_unset=is_patch)
        facilities_ids = update_dict.pop('facilities_ids', None)
        
        # Если есть другие поля для обновления - обновляем основную таблицу
        if update_dict:
            column_names = {c.name for c in self.model.__table__.columns}
            filtered_update_dict = {k: v for k, v in update_dict.items() if k in column_names}
            
            if filtered_update_dict:
                edit_stmt = (
                    update(self.model)
                    .filter_by(**filters_by)
                    .values(**filtered_update_dict)
                )
                await self.session.execute(edit_stmt)
        
        # Обновляем facilities если они переданы
        if facilities_ids is not None or not is_patch:
            # Получаем room_id из filters_by (предполагаем что передается id=room_id)
            room_id = filters_by.get('id')
            if room_id:
                await self.update_room_facilities(room_id, facilities_ids)
