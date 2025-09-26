from fastapi import APIRouter, HTTPException

from src.schemas.bookings import BookingAddRequest
from src.api.dependencies import DBDep, PaginationDep, UserIdDep
from src.services.bookings import BookingService
from src.exceptions import IncorrectDateException, ObjectNotFoundException, AllRoomsAreBookedException


router = APIRouter(prefix="/bookings", tags=["Бронирования"])


@router.post("")
async def create_bookings(
    db: DBDep,
    bookings_data: BookingAddRequest,
    user_id: UserIdDep,
):
    try:
        booking = await BookingService(db).create_booking(bookings_data, user_id)
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail="Номер не найден")
    except AllRoomsAreBookedException as ex:
        raise HTTPException(status_code=409, detail=ex.detail)
    except IncorrectDateException as ex:
        raise HTTPException(status_code=400, detail=ex.detail)

    await db.commit()
    return {"status": "OK", "data": booking}


@router.get("")
async def get_bookings(
    db: DBDep,
    pagination: PaginationDep,
):
    page_size = pagination.page_size or 5
    offset = page_size * (pagination.page_number - 1)

    return await db.bookings.get_all(limit=page_size, offset=offset)


@router.get("/me")
async def get_bookings_me(
    db: DBDep,
    user_id: UserIdDep,
    pagination: PaginationDep,
):
    page_size = pagination.page_size or 5
    offset = page_size * (pagination.page_number - 1)

    return await db.bookings.get_all(user_id=user_id, limit=page_size, offset=offset)
