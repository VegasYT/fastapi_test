from typing import Annotated
 
from fastapi import Depends, HTTPException, Query, Request
from pydantic import BaseModel

from src.services.auth import AuthService
from src.utils.db_manager import DBManager
from src.database import async_session_maker


class PaginationParams(BaseModel):
    page_size: Annotated[int | None, Query(None, ge=1, lt=30, description="Кол-во элементов на странице")]
    page_number: Annotated[int | None, Query(1, ge=1, description="Номер страницы")]


def get_token(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Отсутствует токен")
    return token
    

def get_current_user_id(token: str = Depends(get_token)) -> int:
    data = AuthService().decode_token(token)
    return data["user_id"]


async def get_db():
    async with DBManager(session_factory=async_session_maker) as db:
        yield db


UserIdDep = Annotated[int, Depends(get_current_user_id)]
PaginationDep = Annotated[PaginationParams, Depends()]
DBDep = Annotated[DBManager, Depends(get_db)]