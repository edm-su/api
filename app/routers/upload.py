import hashlib
from collections.abc import Mapping
from io import BytesIO
from typing import IO

import httpx
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from PIL import Image
from starlette import status

from app.auth import get_current_admin
from app.helpers import s3_client
from app.schemas.file import UploadedFile
from app.schemas.upload import ImageURLDTO
from app.settings import settings

router = APIRouter()

max_file_size = 5_000_000  # 5 MB


@router.post(
    "/upload/images",
    tags=["Загрузка", "Посты"],
    summary="Загрузка изображений",
    response_model=UploadedFile,
)
async def upload_image(
    image: UploadFile = File(...),
    admin: Mapping = Depends(get_current_admin),  # noqa: ARG001
) -> dict[str, str]:
    if not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл должен быть изображением",
        )

    if get_file_size(image.file) > max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Файл не должен превышать 5 мб",
        )

    filename = calculate_file_hash_sha224(image.file)
    path = f"images/{filename}.jpeg"

    await convert_and_upload_image(image.file, path)

    return {"file_url": f"{settings.static_url}/{path}", "file_path": path}


@router.post(
    "/upload/image_url",
    tags=["Загрузка", "Посты"],
    summary="Загрузка изображений по ссылке",
    response_model=UploadedFile,
)
async def upload_image_url(
    image_url: ImageURLDTO,
    admin: Mapping = Depends(get_current_admin),  # noqa: ARG001
) -> dict[str, str]:
    async with httpx.AsyncClient() as client:
        h = await client.head(image_url.url)
        header = h.headers
    if not header.get("Content-Type").startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл должен быть изображением",
        )

    if int(header.get("Content-Length")) > max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Файл не должен превышать 5 мб",
        )

    async with httpx.AsyncClient() as client:
        r = await client.get(image_url.url)
        image = BytesIO(r.content)

    if get_file_size(image) > max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Файл не должен превышать 5 мб",
        )

    path = f"images/{calculate_file_hash_sha224(image)}.jpeg"

    await convert_and_upload_image(image, path)
    return {"file_url": f"{settings.static_url}/{path}", "file_path": path}


def calculate_file_hash_sha224(file: IO) -> str:
    file_hash = hashlib.sha224()
    file.seek(0)
    while chunk := file.read(8192):
        file_hash.update(chunk)
    return file_hash.hexdigest()


def get_file_size(file: IO) -> int:
    real_file_size = 0
    file.seek(0)

    for chunk in file:
        real_file_size += len(chunk)

    return real_file_size


async def convert_and_upload_image(file: IO, path: str) -> None:
    image = Image.open(file)
    image = image.convert("RGB")
    jpeg_file = BytesIO()
    image.save(jpeg_file, "JPEG")
    jpeg_file.seek(0)

    async with s3_client() as client:
        await client.put_object(
            Body=jpeg_file,
            Bucket=settings.s3_bucket,
            Key=path,
            ContentType="image/jpeg",
            ACL="public-read",
        )
