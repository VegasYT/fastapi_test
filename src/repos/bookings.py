from sqlalchemy import func, select

from src.schemas.bookings import Booking
from src.models.bookings import BookingsOrm
from src.repos.base import BaseRepository


class BookingsRepository(BaseRepository):
    model = BookingsOrm
    schema = Booking

    