from typing import Annotated
 
from fastapi import Depends, Query
from pydantic import BaseModel


class PaginationParams(BaseModel):
    page_size: Annotated[int | None, Query(None, ge=1, lt=30, description="Кол-во элементов на странице")]
    page_number: Annotated[int | None, Query(1, ge=1, description="Номер страницы")]


PaginationDep = Annotated[PaginationParams, Depends()]