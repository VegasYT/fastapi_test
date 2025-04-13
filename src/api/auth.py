from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError

from src.repos.users import UsersRepository
from src.schemas.users import UserAdd, UserRequestAdd
from src.database import async_session_maker


router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register")
async def register_user(
    data: UserRequestAdd
):
    hashed_password = pwd_context.hash(data.password)
    new_user_data = UserAdd(
        email=data.email, 
        hashed_password=hashed_password, 
        first_name=data.first_name, 
        last_name=data.last_name
    )
    
    async with async_session_maker() as session:
        try:
            user = await UsersRepository(session).add(new_user_data)
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            if "users_email_key" in str(e):
                raise HTTPException(
                    status_code=400,
                    detail="Пользователь с таким email уже существует"
                )
            raise  # повторно вызываем исключение, если это не ошибка уникальности email

    return {"status": "OK"}