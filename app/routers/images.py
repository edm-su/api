from io import BytesIO

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from starlette import status
from PIL import Image
from hashlib import md5

from app import settings
from app.models import User
from app.utils import get_current_admin, s3_client

router = APIRouter()


@router.post('/images/upload', tags=['Изображения', 'Посты'], summary='Загрузка изображения')
def upload_image(folder: str = Query('images', regex='^[a-zA-Z][_\w]+[a-zA-Z]$'), image: UploadFile = File(...),
                 admin: User = Depends(get_current_admin)):
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Файл должен быть изображением')

    image = Image.open(image.file)
    image = image.convert('RGB')
    filename = f'{md5(image.tobytes()).hexdigest()}.jpeg'

    file = BytesIO()
    image.save(file, 'JPEG')
    file.seek(0)
    s3_client().put_object(Body=file, Bucket=settings.S3_BUCKET, Key=f'{folder}/{filename}', ContentType='image/jpeg',
                           ACL='public-read')
    return {"filename": f'{folder}/{filename}'}
