from typing import Mapping

import pytest
from httpx import AsyncClient
from starlette import status

from app.helpers import s3_client
from app.settings import settings
from tests.helpers import create_auth_header


@pytest.mark.asyncio
async def test_upload_image(
        client: AsyncClient,
        admin: Mapping,
) -> None:
    """
    Тест загрузка изображения
    :param client:
    :param admin:
    :return:
    """
    auth_headers = create_auth_header(admin['username'])
    with open('tests/files/test.jpeg', 'rb') as f:
        response = await client.post(
            '/upload/images',
            headers=auth_headers,
            files={
                'image': f
            }
        )

    assert response.status_code == status.HTTP_200_OK
    async with s3_client() as s3:
        assert await s3.head_object(
            Key=response.json()['file_path'],
            Bucket=settings.s3_bucket
        )


@pytest.mark.asyncio
async def test_upload_image_unauthorized(
        client: AsyncClient,
) -> None:
    """
    Тест загрузка изображения без авторизации
    :param client:
    :return:
    """
    with open('tests/files/test.jpeg', 'rb') as f:
        response = await client.post(
            '/upload/images',
            files={
                'image': f
            }
        )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_upload_image_by_user(
        client: AsyncClient,
        user: Mapping,
) -> None:
    """
    Тест загрузка изображения пользователем
    :param client:
    :param user:
    :return:
    """
    auth_headers = create_auth_header(user['username'])
    with open('tests/files/test.jpeg', 'rb') as f:
        response = await client.post(
            '/upload/images',
            files={
                'image': f
            },
            headers=auth_headers
        )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_upload_image_bad_request(
        client: AsyncClient,
        admin: Mapping,
) -> None:
    """
    Тест загрузка изображения без файла
    :param client:
    :param admin:
    :return:
    """
    auth_headers = create_auth_header(admin['username'])
    response = await client.post(
        '/upload/images',
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
