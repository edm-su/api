import typing

import pytest
from httpx import AsyncClient
from starlette import status

from tests.helpers import create_auth_header


####################################
# DELETE /channels/{slug}
####################################
@pytest.mark.asyncio
async def test_delete_channel(
        client: AsyncClient,
        channel_to_be_deleted: typing.Mapping,
        admin: typing.Mapping,
) -> None:
    auth_headers = create_auth_header(admin['username'])
    response = await client.delete(
        f'/channels/{channel_to_be_deleted["slug"]}',
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_channel_without_auth(
        client: AsyncClient,
        channel_to_be_deleted: typing.Mapping,
) -> None:
    response = await client.delete(
        f'/channels/{channel_to_be_deleted["slug"]}')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_delete_channel_by_user(
        client: AsyncClient,
        channel_to_be_deleted: typing.Mapping,
        user: typing.Mapping,
) -> None:
    auth_headers = create_auth_header(user['username'])
    response = await client.delete(
        f'/channels/{channel_to_be_deleted["slug"]}',
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_channel_not_found(
        client: AsyncClient,
        channel_to_be_deleted: typing.Mapping,
        admin: typing.Mapping,
) -> None:
    auth_headers = create_auth_header(admin['username'])
    response = await client.delete(
        f'/channels/{channel_to_be_deleted["slug"]}notfound',
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
