from models.users import UsersOrm
from src.schemas.users import User
from src.repos.base import BaseRepository


class UsersRepository(BaseRepository):
    model = UsersOrm
    schema = User