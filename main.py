from fastapi import FastAPI, Query, Body
import uvicorn
from pydantic import BaseModel
from typing import Optional


app = FastAPI()

# PUT
class HotelUpdate(BaseModel):
    id: int
    title: str
    name: str

# PATCH
class HotelPartialUpdate(BaseModel):
    id: int
    title: Optional[str] = None
    name: Optional[str] = None

hotels = [
    {"id": 1, "title": "Sochi", "name": "сочи"},
    {"id": 2, "title": "Dubai", "name": "дубай"},
]


@app.get("/hotels")
def get_hotels(
        id: int | None = Query(None, description="Айдишник"),
        title: str | None = Query(None, description="Название отеля"),
):
    hotels_ = []
    for hotel in hotels:
        if id and hotel["id"] != id:
            continue
        if title and hotel["title"] != title:
            continue
        hotels_.append(hotel)
    return hotels_


@app.delete("/hotels/{hotel_id}")
def delete_hotel(hotel_id: int):
    global hotels
    hotels = [hotel for hotel in hotels if hotel["id"] != hotel_id]
    return {"status": "OK"}


@app.post("/hotels")
def cerate_hotel(
    title: str = Body(embed=True),
):
    global hotels

    hotels.append({
        "id": hotels[-1]["id"] + 1, 
        "title": title,
        })
    
    return {"status": "ok"}


@app.put("/hotels")
def edit_hotel(hotel_data: HotelUpdate):
    for hotel in hotels:
        if hotel["id"] == hotel_data.id:
            hotel["title"] = hotel_data.title
            hotel["name"] = hotel_data.name

    return {"status": "OK"}
    

@app.patch("/hotels")
def partial_edit_hotel(hotel_data: HotelPartialUpdate):
    for hotel in hotels:
        if hotel["id"] == hotel_data.id:
            update_data = hotel_data.dict(exclude_unset=True)
            hotel.update(update_data)

    return {"status": "OK"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)