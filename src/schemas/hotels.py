from pydantic import BaseModel, Field


class HotelAdd(BaseModel):
    title: str = Field(min_length=1, max_length=35, description="Название отеля")
    location: str = Field(min_length=1, max_length=100, description="Местоположение отеля")


class Hotel(HotelAdd):
    id: int


class HotelPATCH(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=35, description="Название отеля")
    location: str | None = Field(None, min_length=1, max_length=100, description="Местоположение отеля")
