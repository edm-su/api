import typing

import pytest
from httpx import AsyncClient
from slugify import slugify
from starlette import status

from app.crud import channel as channel_crud
from tests.helpers import create_auth_header


@pytest.mark.asyncio
async def test_delete_channel(
        client: AsyncClient,
        channel: typing.Mapping,
        admin: typing.Mapping,
) -> None:
    auth_headers = create_auth_header(admin['username'])
    response = await client.delete(
        f'/channels/{channel["slug"]}',
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_channel_without_auth(
        client: AsyncClient,
        channel: typing.Mapping,
) -> None:
    response = await client.delete(
        f'/channels/{channel["slug"]}')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_delete_channel_by_user(
        client: AsyncClient,
        channel: typing.Mapping,
        user: typing.Mapping,
) -> None:
    auth_headers = create_auth_header(user['username'])
    response = await client.delete(
        f'/channels/{channel["slug"]}',
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_channel_not_found(
        client: AsyncClient,
        channel: typing.Mapping,
        admin: typing.Mapping,
) -> None:
    auth_headers = create_auth_header(admin['username'])
    response = await client.delete(
        f'/channels/{channel["slug"]}notfound',
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_create_channel(
        client: AsyncClient,
        channel_data: dict,
        admin: typing.Mapping,
) -> None:
    auth_headers = create_auth_header(admin['username'])
    response = await client.post(
        '/channels',
        json=channel_data,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    db_channel = await channel_crud.get_channel_by_slug(data['slug'])
    assert db_channel
    assert db_channel['id'] == data['id']


@pytest.mark.asyncio
async def test_create_by_guest(
        client: AsyncClient,
        channel_data: dict,
) -> None:
    response = await client.post(
        '/channels',
        json=channel_data,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    slug = slugify(channel_data['name'])
    assert not await channel_crud.get_channel_by_slug(slug)


@pytest.mark.asyncio
async def test_create_by_user(
        client: AsyncClient,
        channel_data: dict,
        user: typing.Mapping,
) -> None:
    auth_headers = create_auth_header(user['username'])
    response = await client.post(
        '/channels',
        json=channel_data,
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    slug = slugify(channel_data['name'])
    assert not await channel_crud.get_channel_by_slug(slug)
