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
    booking_read = await db.bookings.get_one_or_none(id=booking.id)
    assert booking_read
    assert booking_read.room_id == room_id

    # Update
    booking_edit_data = BookingAddInternal(
        user_id=user_id,
        room_id=room_id,
        date_from=date(year=2025, month=7, day=10),
        date_to=date(year=2025, month=8, day=20),
        price=100,
    )
    await db.bookings.edit(update_data=booking_edit_data, is_patch=False, id=booking.id)
    booking_edit_read = await db.bookings.get_one_or_none(id=booking_read.id)
    assert booking_edit_read.date_from == date(year=2025, month=7, day=10)

    # Delete
    await db.bookings.delete(id=booking.id)
    booking_read = await db.bookings.get_one_or_none(id=booking.id)
    assert booking_read is None

    await db.commit()