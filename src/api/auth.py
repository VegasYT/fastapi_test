from fastapi import APIRouter, HTTPException, Response

from src.exceptions import UniqueViolationException
from src.api.dependencies import DBDep, UserIdDep
from src.schemas.users import UserAdd, UserRequestAdd, UserRequestLogin
from src.services.auth import AuthService


router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


@router.post("/register")
async def register_user(db: DBDep, data: UserRequestAdd):
    try:
        await AuthService(db).register(data)
    except UniqueViolationException:
        raise HTTPException(status_code=409, detail="Такой пользователь уже сущестувет")

    await db.commit()
    return {"status": "OK"}


@router.post("/login")
async def login_user(db: DBDep, data: UserRequestLogin, response: Response):
    user = await AuthService(db).login(data)
    access_token = AuthService().create_access_token({"user_id": user.id})
    response.set_cookie("access_token", access_token)
    return {"access_token": access_token}


@router.get("/me")
async def get_me(db: DBDep, user_id: UserIdDep):
    user = await AuthService(db).me(user_id)
    return user


@router.post("/logout")
async def logout_user(db: DBDep, response: Response):
    response.delete_cookie("access_token")

    await db.commit()
    return {"status": "ok"}
