from pydantic import BaseModel
from datetime import date


class BookingAddRequest(BaseModel):
    room_id: int
    date_from: date
    date_to: date
    # price:


class BookingAddInternal(BookingAddRequest):
    user_id: int
    price: int


class Booking(BookingAddRequest):
    id: int


class BookingGetAllResponse(BookingAddRequest):
    id: int
    user_id: int
    room_id: int
    date_from: date
    date_to: date
    price: int
