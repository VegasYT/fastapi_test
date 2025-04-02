from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
 
from src.repos.users import UsersRepository
from src.schemas.users import UserAdd, UserRequestAdd
from src.database import async_session_maker

router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register")
async def register_user(
    data: UserRequestAdd
):
    async with async_session_maker() as session:
        existing_user = await UsersRepository(session).get_one_or_none(email=data.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Пользователь с таким email уже существует"
            )

        hashed_password = pwd_context.hash(data.password)
        new_user_data = UserAdd(
            email=data.email, 
            hashed_password=hashed_password, 
            first_name=data.first_name, 
            last_name=data.last_name
        )

        user = await UsersRepository(session).add(new_user_data)
        await session.commit()

    return {"status": "OK"}