from fastapi import Body, APIRouter
from fastapi_cache.decorator import cache

from src.schemas.facilities import FacilityAdd
from src.api.dependencies import DBDep, PaginationDep
from src.tasks.tasks import test_task # noqa
 

router = APIRouter(prefix="/facilities", tags=["Удобства"])
 

@router.get("")
@cache(expire=10)
async def get_facilities(
    db: DBDep,
    pagination: PaginationDep,
):
    page_size = pagination.page_size or 5
    offset = page_size * (pagination.page_number - 1)

    return await db.facilities.get_filtered_by_pagination(
        limit=page_size, 
        offset=offset,
    )


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

    # test_task.delay()

    return {"status": "OK", "data": facility}


