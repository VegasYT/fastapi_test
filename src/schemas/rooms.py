from pydantic import BaseModel


class RoomAdd(BaseModel):
    hotel_id: int
    title: str
    description: str
    price: int
    quantity: int
    facilities_ids: list[int] | None = None


class Room(RoomAdd):
    id: int


class RoomPATCH(BaseModel):
    hotel_id: int | None = None
    title: str | None = None
    description: str | None = None
    price: int | None = None
    quantity: int | None = None
    facilities_ids: list[int] | None = None