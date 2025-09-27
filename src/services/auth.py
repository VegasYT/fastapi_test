from fastapi import HTTPException
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt

from src.schemas.users import UserAdd
from src.services.base import BaseService
from src.config import settings


class AuthService(BaseService):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode |= {"exp": expire}
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    def hashed_password(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(jwt=token, algorithms=["HS256"], key=settings.JWT_SECRET_KEY)
        except jwt.exceptions.DecodeError:
            raise HTTPException(status_code=401, detail="Неверный токен")

    async def register(self, data):
        hashed_password = AuthService().pwd_context.hash(data.password)
        new_user_data = UserAdd(
            email=data.email,
            hashed_password=hashed_password,
            first_name=data.first_name,
            last_name=data.last_name,
        )

        await self.db.users.add(new_user_data)

    async def login(self, data):
        user = await self.db.users.get_user_with_hashed_password(email=data.email)

        if not user:
            raise HTTPException(status_code=401, detail="Неверный логин или пароль")

        if not AuthService().verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Неверный логин или пароль")

        await self.db.commit()

        return user
    
    async def me(self, user_id):
        user = await self.db.users.get_one_or_none(id=user_id)
        return user
