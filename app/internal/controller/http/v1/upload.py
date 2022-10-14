import hashlib
from typing import IO, Mapping

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from starlette import status

from app.auth import get_current_admin
from app.internal.entity.upload import ImageURL, ImageURLs
from app.internal.usecase.exceptions.upload import UploadError
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
    admin: Mapping = Depends(get_current_admin),
) -> ImageURLs:
    if not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл должен быть изображением",
        )

    use_case = UploadImageUseCase(S3UploadRepository(), image.file)
    try:
        urls = await use_case.execute()
    except UploadError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    return urls


@router.post(
    "/image_url",
    tags=["Загрузка", "Посты"],
    summary="Загрузка изображений по ссылке",
    response_model=ImageURLs,
)
async def upload_image_url(
    image_url: ImageURL,
    admin: Mapping = Depends(get_current_admin),
) -> ImageURLs:
    use_case = UploadImageURLUseCase(S3UploadRepository(), image_url)
    try:
        urls = await use_case.execute()
    except UploadError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    return urls


def get_md5_hash(file: IO) -> str:
    md5 = hashlib.md5()
    file.seek(0)
    while chunk := file.read(8192):
        md5.update(chunk)
    return md5.hexdigest()
