from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from starlette import status

from app.internal.controller.http.v1.dependencies.auth import get_current_admin
from app.internal.entity.upload import ImageURL, ImageURLs
from app.internal.entity.user import User
from app.internal.usecase.exceptions.upload import (
    FileIsTooLargeError,
    UploadError,
)
from app.internal.usecase.repository.upload import S3UploadRepository
from app.internal.usecase.upload import (
    UploadImageURLUseCase,
    UploadImageUseCase,
)

router = APIRouter()


@router.post(
    "/images",
    tags=["Загрузка", "Посты"],
    summary="Загрузка изображений",
    response_model=ImageURLs,
)
async def upload_image(
    image: UploadFile = File(...),
    _: User = Depends(get_current_admin),
) -> ImageURLs:
    if image.content_type is None or not image.content_type.startswith(
        "image/",
    ):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Файл должен быть изображением",
        )

    use_case = UploadImageUseCase(S3UploadRepository(), image.file)
    try:
        urls = await use_case.execute()
    except FileIsTooLargeError as e:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(e),
        ) from e
    except UploadError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    return urls


@router.post(
    "/image_url",
    tags=["Загрузка", "Посты"],
    summary="Загрузка изображений по ссылке",
    response_model=ImageURLs,
)
async def upload_image_url(
    image_url: ImageURL,
    _: User = Depends(get_current_admin),
) -> ImageURLs:
    use_case = UploadImageURLUseCase(S3UploadRepository(), image_url)
    try:
        urls = await use_case.execute()
    except FileIsTooLargeError as e:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(e),
        ) from e
    except UploadError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    return urls
