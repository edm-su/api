from datetime import date, timedelta
from typing import Mapping

import pytest
from httpx import AsyncClient
from starlette import status

from app.crud import livestream as livestream_crud
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
    assert await livestream_crud.find_one(data['id'])


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
    assert not await livestream_crud.find_one(title=livestream_data['title'])

    response = await client.post(
        '/livestreams',
        json=livestream_data,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert not await livestream_crud.find_one(title=livestream_data['title'])


@pytest.mark.asyncio
async def test_get_livestreams(
        client: AsyncClient,
        livestream: Mapping,
        livestream_in_a_month: Mapping,
) -> None:
    response = await client.get('/livestreams')

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data[0]['title'] == livestream['title']
    assert len(data) == 1


@pytest.mark.asyncio
async def test_period_excess_error(
        client: AsyncClient,
) -> None:
    start_date = date.today() - timedelta(days=20)
    end_date = start_date + timedelta(days=20)
    response = await client.get(
        '/livestreams',
        params={
            'start': start_date.isoformat(),
            'end_date': end_date.isoformat(),
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()['detail'] == 'Период не может превышать 45 дней'
