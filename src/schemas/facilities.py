from pydantic import BaseModel, Field


class FacilityAdd(BaseModel):
    title: str = Field(min_length=1, max_length=35, description="Название удобства")


class Facility(FacilityAdd):
    id: int


class RoomFacilityAdd(BaseModel):
    room_id: int
    facility_id: int


class RoomFacility(RoomFacilityAdd):
    id: int
