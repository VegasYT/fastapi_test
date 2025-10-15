from pydantic import BaseModel, Field

from src.schemas.facilities import Facility


class RoomAdd(BaseModel):
    hotel_id: int
    title: str = Field(min_length=1, max_length=35)
    description: str = Field(min_length=1, max_length=100)
    price: int = Field(gt=0, le=2147483647)
    quantity: int = Field(gt=0, le=2147483647, description="Количество номеров")
    facilities_ids: list[int] | None = None


class Room(BaseModel):
    id: int
    hotel_id: int
    title: str
    description: str | None = None
    price: int
    quantity: int


class RoomWithRels(Room):
    facilities: list[Facility]


class RoomPATCH(BaseModel):
    hotel_id: int | None = None
    title: str | None = None
    description: str | None = None
    price: int | None = Field(None, gt=0, le=2147483647)
    quantity: int | None = Field(None, gt=0, le=2147483647, description="Количество номеров")
    facilities_ids: list[int] | None = None
