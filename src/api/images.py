import shutil

from fastapi import APIRouter, UploadFile, File, HTTPException

from src.services.images import ImagesService


router = APIRouter(prefix="/images", tags=["Изображения отелей"])

# Разрешенные типы изображений
ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/gif",
    "image/webp",
}


@router.post("")
def upload_image(
    file: UploadFile = File(
        ...,
        description="Загрузить изображение отеля (JPEG, PNG, GIF, WebP)",
        media_type="image/jpeg,image/png,image/gif,image/webp"
    )
):
    # Проверяем тип файла
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Недопустимый тип файла: {file.content_type}. "
                   f"Разрешены только изображения: JPEG, PNG, GIF, WebP"
        )

    # # Дополнительная проверка расширения файла
    # if file.filename:
    #     extension = file.filename.lower().split('.')[-1]
    #     if extension not in {'jpg', 'jpeg', 'png', 'gif', 'webp'}:
    #         raise HTTPException(
    #             status_code=400,
    #             detail=f"Недопустимое расширение файла: .{extension}. "
    #                    f"Разрешены только: .jpg, .jpeg, .png, .gif, .webp"
    #         )

    ImagesService().upload_image(file)
