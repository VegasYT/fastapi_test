from pydantic import BaseModel


class FacilityAdd(BaseModel):
    title: str


class Facility(FacilityAdd):
    id: int


# class FacilityPATCH(BaseModel):
#     title: str | None = None
#     location: str | None = None
