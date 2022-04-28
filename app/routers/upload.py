import re
from io import BytesIO
from time import time
from typing import Mapping, IO

from PIL import Image
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    HTTPException,
)
from starlette import status

from app.auth import get_current_admin
from app.helpers import s3_client
from app.schemas.file import UploadedFile
from app.settings import settings

router = APIRouter()


@router.post(
    '/upload/images',
    tags=['Загрузка', 'Посты'],
    summary='Загрузка изображений',
    response_model=UploadedFile,
)
async def upload_image(
        image: UploadFile = File(...),
        admin: Mapping = Depends(get_current_admin),
) -> dict[str, str]:
    if not image.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Файл должен быть изображением',
        )

    if get_file_size(image.file) > 5_000_000:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail='Файл не должен превышать 5 мб',
        )

    filename = re.search(r'[\wа-яА-Я_-]+', image.filename)
    filename = f'{int(time())}-{filename.group(0)}'
    path = f'images/{filename}.jpeg'

    await convert_and_upload_image(image.file, path)

    return {'file_url': f'{settings.static_url}/{path}', 'file_path': path}


def get_file_size(file: IO) -> int:
    real_file_size = 0

    for chunk in file:
        real_file_size += len(chunk)

    return real_file_size


async def convert_and_upload_image(file: IO, path: str) -> None:
    image = Image.open(file)
    image = image.convert('RGB')
    jpeg_file = BytesIO()
    image.save(jpeg_file, 'JPEG')
    jpeg_file.seek(0)

    async with s3_client() as client:
        await client.put_object(
            Body=jpeg_file,
            Bucket=settings.s3_bucket,
            Key=path,
            ContentType='image/jpeg',
            ACL='public-read',
        )
