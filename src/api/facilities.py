import json

from fastapi import Body, APIRouter, Body

from src.schemas.facilities import FacilityAdd
from src.api.dependencies import DBDep, PaginationDep
from src.init import redis_manager
 

router = APIRouter(prefix="/facilities", tags=["Удобства"])
 

@router.get("")
async def get_facilities(
    db: DBDep,
    pagination: PaginationDep,
):
    # TODO: Учесть пагинацию в кешировании
    page_size = pagination.page_size or 5
    offset = page_size * (pagination.page_number - 1)

    facilities_from_cache = await redis_manager.get("facilities")
    if not facilities_from_cache:
        print("ИДУ В БАЗУ ДАННЫХ")
        facilities = await db.facilities.get_filtered_by_pagination(limit=page_size, offset=offset,)
        facilities_schemas: list[dict] = [f.model_dump() for f in facilities]
        facilities_json = json.dumps(facilities_schemas)
        await redis_manager.set("facilities", facilities_json, 10)

        return facilities
    else:
        facilities_dicts = json.loads(facilities_from_cache)
        return facilities_dicts


@router.post("")
async def create_facilities(
    db: DBDep,
    facility_data: FacilityAdd = Body(openapi_examples={
        "1": {
            "title": "Завтрак",
            "value": {
                "title": "Завтрак",
            }
        },
        "2": {
            "summary": "Wi-Fi",
            "value": {
                "title": "Wi-Fi",
            }
        }
    }),
):
    facility = await db.facilities.add(facility_data)
    await db.commit()

    return {"status": "OK", "data": facility}


