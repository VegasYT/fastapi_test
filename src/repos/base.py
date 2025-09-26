from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import Sequence, delete, func, insert, select, update
from sqlalchemy.exc import NoResultFound, IntegrityError

from src.repos.mappers.base import DataMapper
from src.exceptions import ObjectNotFoundException, UniqueViolationException


class BaseRepository:
    model = None
    mapper: DataMapper = None

    def __init__(self, session):
        self.session = session

    async def _validate_single_object(self, **filters_by) -> None:
        count = await self.session.scalar(
            select(func.count()).select_from(self.model).filter_by(**filters_by)
        )

        if count == 0:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} not found")
        if count > 1:
            raise HTTPException(
                status_code=422,
                detail=f"Несколько объектов {self.model.__name__} соответствуют критериям",
            )

    async def get_filtered(self, *filter, **filter_by):
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        result = await self.session.execute(query)

        return [self.mapper.map_to_domain_entity(obj) for obj in result.scalars().all()]

    async def get_all(self, *args, **kwargs):
        return await self.get_filtered()

    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)

        obj = result.scalars().one_or_none()
        if obj is None:
            return None

        return self.mapper.map_to_domain_entity(obj)
    
    async def get_one(self, **filter_by) -> BaseModel:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        try:
            model = result.scalar_one()
        except NoResultFound:
            raise ObjectNotFoundException
        return self.mapper.map_to_domain_entity(model)

    async def add(self, add_data: BaseModel):
        # Получаем имена колонок модели
        column_names = {c.name for c in self.model.__table__.columns}

        # Исключаем поля, которых нет в колонках модели
        add_data_dict = add_data.model_dump(
            exclude={k for k in add_data.model_dump().keys() if k not in column_names}
        )

        add_stmt = insert(self.model).values(**add_data_dict).returning(self.model)

        try:
            result = await self.session.execute(add_stmt)
        except IntegrityError as e:
            if "UniqueViolationError" in str(e.orig):
                raise UniqueViolationException
            elif "ForeignKeyViolationError" in str(e.orig):
                raise ObjectNotFoundException

        obj = result.scalar_one()
        return obj

    async def add_bulk(self, data: Sequence[BaseModel]):
        # Получаем имена колонок модели
        column_names = {c.name for c in self.model.__table__.columns}

        # Фильтруем данные, исключая поля, которых нет в модели
        filtered_data = [
            {k: v for k, v in item.model_dump().items() if k in column_names} for item in data
        ]

        add_data_stmt = insert(self.model).values(filtered_data)
        await self.session.execute(add_data_stmt)

    async def edit(self, update_data: BaseModel, is_patch: bool = False, **filters_by) -> None:
        await self._validate_single_object(**filters_by)

        # Получаем имена колонок модели
        column_names = {c.name for c in self.model.__table__.columns}
        # Исключаем поля, которых нет в колонках модели
        update_data_dict = update_data.model_dump(
            exclude={k for k in update_data.model_dump().keys() if k not in column_names},
            exclude_unset=is_patch,
        )

        edit_stmt = update(self.model).filter_by(**filters_by).values(**update_data_dict)

        try:
            await self.session.execute(edit_stmt)
        except IntegrityError as e:
            if "UniqueViolationError" in str(e.orig):
                raise UniqueViolationException
            elif "ForeignKeyViolationError" in str(e.orig):
                raise ObjectNotFoundException
            
    async def delete(self, **filters_by) -> None:
        await self._validate_single_object(**filters_by)

        delete_stmt = delete(self.model).filter_by(**filters_by)

        try:
            await self.session.execute(delete_stmt)
        except IntegrityError as e:
            if "UniqueViolationError" in str(e.orig):
                raise UniqueViolationException
            elif "ForeignKeyViolationError" in str(e.orig):
                raise ObjectNotFoundException
