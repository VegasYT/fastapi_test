from fastapi import APIRouter

from src.schemas.bookings import BookingAddRequest
from src.api.dependencies import DBDep, UserIdDep
from src.services.bookings import BookingService


router = APIRouter(prefix="/bookings", tags=["Бронирования"])


@router.post("")
async def create_bookings(
    db: DBDep,
    bookings_data: BookingAddRequest,
    user_id: UserIdDep,
):
    booking = await BookingService(db).create_booking(bookings_data, user_id)

    return {"status": "OK", "data": booking}