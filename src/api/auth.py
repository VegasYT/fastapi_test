from fastapi import APIRouter, HTTPException, Response
 
from src.repos.users import UsersRepository
from src.schemas.users import UserAdd, UserRequestAdd, UserRequestLogin
from src.database import async_session_maker


router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])



def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)



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
        existing_user = await UsersRepository(session).get_one_or_none(email=data.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Пользователь с таким email уже существует"
            )
        
        user = await UsersRepository(session).add(new_user_data)
        await session.commit()

    return {"status": "OK"}


@router.post("/login")
async def login_user(
    data: UserRequestLogin,
    response: Response
):
    async with async_session_maker() as session:
        user = await UsersRepository(session).get_user_with_hashed_password(email=data.email)

        if not user:
            raise HTTPException(status_code=401, detail="Неверный логин или пароль")
        
        if not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Неверный логин или пароль")
        
        access_token = create_access_token({"user_id": user.id})
        response.set_cookie("access_token", access_token)

        return {"access_token": access_token}