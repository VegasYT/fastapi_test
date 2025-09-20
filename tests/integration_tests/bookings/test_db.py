from datetime import date
from src.schemas.bookings import BookingAddInternal


async def test_booking_crud(db):
    # Create
    user_id = (await db.users.get_all())[0].id
    room_id = (await db.rooms.get_all())[0].id
    booking_data = BookingAddInternal(
        user_id=user_id,
        room_id=room_id,
        date_from=date(year=2025, month=8, day=10),
        date_to=date(year=2025, month=8, day=20),
        price=100,
    )
    booking = await db.bookings.add(booking_data)

    # Read
    await db.bookings.get_one_or_none(id=booking.id)

    # Update
    booking_edit_data = BookingAddInternal(
        user_id=user_id,
        room_id=room_id,
        date_from=date(year=2025, month=8, day=10),
        date_to=date(year=2025, month=8, day=20),
        price=200,
    )
    await db.bookings.edit(update_data=booking_edit_data, is_patch=False, id=booking.id)

    # Delete
    await db.bookings.delete(id=booking.id)

    await db.commit()