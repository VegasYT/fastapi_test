from fastapi import APIRouter, HTTPException, Response
 
from src.api.dependencies import DBDep, UserIdDep
from src.repos.users import UsersRepository
from src.schemas.users import UserAdd, UserRequestAdd, UserRequestLogin
from src.database import async_session_maker
from src.services.auth import AuthService


router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


@router.post("/register")
async def register_user(
    db: DBDep,
    data: UserRequestAdd
):
    hashed_password = AuthService().pwd_context.hash(data.password)
    new_user_data = UserAdd(
        email=data.email, 
        hashed_password=hashed_password, 
        first_name=data.first_name, 
        last_name=data.last_name
    )

    existing_user = await db.users.get_one_or_none(email=data.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким email уже существует"
        )
    
    user = await db.users.add(new_user_data)

    return {"status": "OK"}


@router.post("/login")
async def login_user(
    db: DBDep,
    data: UserRequestLogin,
    response: Response
):
    user = await db.users.get_user_with_hashed_password(email=data.email)

    if not user:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    
    if not AuthService().verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    
    access_token = AuthService().create_access_token({"user_id": user.id})
    response.set_cookie("access_token", access_token)

    return {"access_token": access_token}
    

@router.get("/me")
async def get_me(
    db: DBDep,
    user_id: UserIdDep
):
    user = await db.users.get_one_or_none(id=user_id)
    return user


@router.post("/logout")
async def logout_user(
    db: DBDep,
    response: Response
):
    response.delete_cookie("access_token")
    
    return {"status": "ok"}