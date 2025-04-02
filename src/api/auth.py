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