from typing import Mapping

import pytest
from httpx import AsyncClient
from starlette import status

from app.crud import livestream
from app.schemas.livestreams import LiveStream
from tests.helpers import create_auth_header


@pytest.mark.asyncio
async def test_create_livestream(
        client: AsyncClient,
        livestream_data: dict,
        admin: Mapping,
) -> None:
    headers = create_auth_header(admin['username'])
    response = await client.post(
        '/livestreams',
        json=livestream_data,
        headers=headers,
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert LiveStream.validate(data)
    assert await livestream.find_one(data['id'])


@pytest.mark.asyncio
async def test_disallow_creation_livestream_without_privileges(
        client: AsyncClient,
        livestream_data: dict,
        user: Mapping,
) -> None:
    headers = create_auth_header(user['username'])
    response = await client.post(
        '/livestreams',
        json=livestream_data,
        headers=headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not await livestream.find_one(title=livestream_data['title'])

    response = await client.post(
        '/livestreams',
        json=livestream_data,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert not await livestream.find_one(title=livestream_data['title'])
