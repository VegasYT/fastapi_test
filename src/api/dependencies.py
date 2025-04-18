from typing import Annotated
 
from fastapi import Depends, HTTPException, Query, Request
from pydantic import BaseModel

from src.services.auth import AuthService


class PaginationParams(BaseModel):
    page_size: Annotated[int | None, Query(None, ge=1, lt=30, description="Кол-во элементов на странице")]
    page_number: Annotated[int | None, Query(1, ge=1, description="Номер страницы")]


PaginationDep = Annotated[PaginationParams, Depends()]

def get_token(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Отсутствует токен")
    return token
    

def get_current_user_id(token: str = Depends(get_token)):
    data = AuthService().decode_token(token)
    user_id = data["user_id"]
    

UserIdDep = Annotated[int, Depends(get_current_user_id)]