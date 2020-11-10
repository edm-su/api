import re
from io import BytesIO
from time import time
from typing import Mapping, Dict, IO

from PIL import Image
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    HTTPException,
)
from starlette import status

from app import settings
from app.auth import get_current_admin
from app.helpers import s3_client
from app.schemas.file import UploadedFile

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
) -> Dict[str, str]:
    if not image.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Файл должен быть изображением',
        )

    filename = re.search(r'[\wа-яА-Я_-]+', image.filename)
    filename = f'{int(time())}-{filename.group(0)}'  # type: ignore
    path = f'images/{filename}.jpeg'

    convert_and_upload_image(image.file, path)
    return {'file_url': f'{settings.STATIC_URL}/{path}', 'file_path': path}


def convert_and_upload_image(file: IO, path: str) -> None:
    image = Image.open(file)
    image = image.convert('RGB')
    file = BytesIO()
    image.save(file, 'JPEG')
    file.seek(0)

    s3_client().put_object(
        Body=file,
        Bucket=settings.S3_BUCKET,
        Key=path,
        ContentType='image/jpeg',
        ACL='public-read',
    )
