from pydantic import EmailStr
from sqlalchemy import select

from src.models.users import UsersOrm
from src.schemas.users import User, UserWitchHashedPassword
from src.repos.base import BaseRepository


class UsersRepository(BaseRepository):
    model = UsersOrm
    schema = User

    async def get_user_with_hashed_password(self, email: EmailStr):
        query = (
            select(self.model)
            .filter_by(email=email)
        )
        result = await self.session.execute(query)

        obj = result.scalars().one_or_none()
        if not obj:
            return None
    
        return UserWitchHashedPassword.model_validate(obj, from_attributes=True)