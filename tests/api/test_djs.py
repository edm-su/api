from typing import Mapping

import pytest
from httpx import AsyncClient
from starlette import status

from app.crud import dj as dj_crud
from app.schemas.dj import DJ
from tests.helpers import create_auth_header


@pytest.mark.asyncio
async def test_create_dj(
        client: AsyncClient,
        dj_data: dict,
        admin: Mapping,
) -> None:
    """
    Создание пользователя
    :param client:
    :param dj_data:
    :param admin:
    :return:
    """
    auth_headers = create_auth_header(admin['username'])
    response = await client.post('/djs', json=dj_data, headers=auth_headers)
    data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert await dj_crud.find(data['id'])
    assert DJ.validate(data)
    for k, v in dj_data.items():
        assert data[k] == v


@pytest.mark.asyncio
async def test_create_group(
        client: AsyncClient,
        group_data: dict,
        admin: Mapping,
        dj: Mapping,
) -> None:
    """
    Создание группы
    :param client:
    :param group_data:
    :param admin:
    :return:
    """
    auth_headers = create_auth_header(admin['username'])
    response = await client.post('/djs', json=group_data, headers=auth_headers)
    data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert await dj_crud.find(data['id'])
    assert DJ.validate(data)
    assert data['is_group']
    assert data['group_members']


@pytest.mark.asyncio
async def test_prohibit_adding_by_user(
        client: AsyncClient,
        dj_data: dict,
        user: Mapping,
) -> None:
    """
    Запрет создания DJ пользователям
    :param client:
    :param dj_data:
    :param user:
    :return:
    """
    auth_headers = create_auth_header(user['username'])
    response = await client.post('/djs', json=dj_data, headers=auth_headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert await dj_crud.find(name=dj_data['name']) is None


@pytest.mark.asyncio
async def test_prohibit_adding_by_guest(
        client: AsyncClient,
        dj_data: dict,
) -> None:
    """
    Запрет создания DJ гостем
    :param client:
    :param dj_data:
    :return:
    """
    response = await client.post('/djs', json=dj_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert await dj_crud.find(name=dj_data['name']) is None
