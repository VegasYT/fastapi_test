from src.api.dependencies import PaginationDep, UserIdDep
from src.schemas.bookings import BookingAddInternal, BookingAddRequest


class BookingService:
    def __init__(self, db):
        self.db = db

    async def create_booking(
        self,
        booking_data: BookingAddRequest,
        user_id: int,
    ):
        room_price = (await self.db.rooms.get_one(id=booking_data.room_id)).price

        internal_data = BookingAddInternal(
            **booking_data.model_dump(),
            user_id=user_id,
            price=room_price,
        )

        room = await self.db.rooms.get_one_or_none(id=booking_data.room_id)

        res = await self.db.bookings.add_booking(internal_data, room.hotel_id)

        await self.db.commit()
        return res


    async def get_bookings(
        self,
        pagination: PaginationDep,
    ):
        page_size = pagination.page_size or 5
        offset = page_size * (pagination.page_number - 1)

        return await self.db.bookings.get_all(limit=page_size, offset=offset)

    async def get_bookings_me(
        self,
        user_id: UserIdDep,
        pagination: PaginationDep,
    ):
        page_size = pagination.page_size or 5
        offset = page_size * (pagination.page_number - 1)

        return await self.db.bookings.get_all(user_id=user_id, limit=page_size, offset=offset)
