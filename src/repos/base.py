from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import delete, func, insert, select, update


class BaseRepository:
    model = None
    schema: BaseModel = None

    def __init__(self, session):
        self.session = session

    async def _validate_single_object(self, **filters_by) -> None:
        count = await self.session.scalar(
            select(func.count())
            .select_from(self.model)
            .filter_by(**filters_by)
        )

        if count == 0:
            raise HTTPException(
                status_code=404,
                detail=f"{self.model.__name__} not found"
            )
        if count > 1:
            raise HTTPException(
                status_code=422,
                detail=f"Несколько объектов {self.model.__name__} соответствуют критериям"
            )

    async def get_all(self, *args, **kwargs):
        query = select(self.model)
        result = await self.session.execute(query)

        return [self.schema.model_validate(obj, from_attributes=True) for obj in result.scalars().all()]

    async def get_one_or_none(self, **filter_by):
        query = (
            select(self.model)
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        obj = result.scalars().one_or_none()
        if obj is None:
            return None
        
        return self.schema.model_validate(obj, from_attributes=True)

    async def add(self, add_data: BaseModel):
        add_stmt = (
            insert(self.model)
            .values(**add_data.model_dump())
            .returning(self.model)
        )

        result = await self.session.execute(add_stmt)
        return result.scalar_one()

    async def edit(self, update_data: BaseModel, is_patch: bool = False, **filters_by) -> None:
        await self._validate_single_object(**filters_by)

        edit_stmt = (
            update(self.model)
            .filter_by(**filters_by)
            .values(**update_data.model_dump(exclude_unset=is_patch))
        )

        await self.session.execute(edit_stmt)

    async def delete(self, **filters_by) -> None:
        await self._validate_single_object(**filters_by)

        delete_stmt = (
            delete(self.model)
            .filter_by(**filters_by)
        )

        await self.session.execute(delete_stmt)
