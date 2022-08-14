from collections.abc import Mapping

import pytest
from httpx import AsyncClient
from starlette import status

from app.crud import dj as dj_crud
from app.schemas.dj import (
    DJ,
    CreateDJ,
)
from tests.helpers import create_auth_header


@pytest.mark.asyncio()
async def test_create_dj(
    client: AsyncClient,
    dj_data: CreateDJ,
    admin: Mapping,
) -> None:
    """
    Создание диджея
    :param client:
    :param dj_data:
    :param admin:
    :return:
    """
    auth_headers = create_auth_header(admin["username"])
    response = await client.post(
        "/djs",
        content=dj_data.json(),
        headers=auth_headers,
    )
    data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert await dj_crud.find(data["id"])
    assert DJ.validate(data)

    response = await client.post(
        "/djs",
        content=dj_data.json(),
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    data = response.json()
    detail = data["detail"]
    assert detail["name"] == "Такой dj уже существует"
    assert detail["slug"] == "Такой slug уже существует"


@pytest.mark.asyncio()
async def test_create_group(
    client: AsyncClient,
    group_data: CreateDJ,
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
    auth_headers = create_auth_header(admin["username"])
    response = await client.post(
        "/djs",
        content=group_data.json(),
        headers=auth_headers,
    )
    data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert await dj_crud.find(data["id"])
    assert DJ.validate(data)
    assert data["is_group"]
    assert data["group_members"]


@pytest.mark.asyncio()
async def test_prohibit_adding_by_user(
    client: AsyncClient,
    dj_data: CreateDJ,
    user: Mapping,
) -> None:
    """
    Запрет создания DJ пользователям
    :param client:
    :param dj_data:
    :param user:
    :return:
    """
    auth_headers = create_auth_header(user["username"])
    response = await client.post(
        "/djs",
        content=dj_data.json(),
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert await dj_crud.find(name=dj_data.name) is None


@pytest.mark.asyncio()
async def test_prohibit_adding_by_guest(
    client: AsyncClient,
    dj_data: CreateDJ,
) -> None:
    """
    Запрет создания DJ гостем
    :param client:
    :param dj_data:
    :return:
    """
    response = await client.post("/djs", content=dj_data.json())

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert await dj_crud.find(name=dj_data.name) is None


@pytest.mark.asyncio()
async def test_delete(
    client: AsyncClient,
    admin: Mapping,
    dj: Mapping,
) -> None:
    """
    Удаление DJ
    :param client:
    :param admin:
    :param dj:
    :return:
    """
    headers = create_auth_header(admin["username"])
    response = await client.delete(f'/djs/{dj["slug"]}', headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert await dj_crud.find(id_=dj["id"]) is None


@pytest.mark.asyncio()
async def test_prohibit_delete(
    client: AsyncClient,
    user: Mapping,
    dj: Mapping,
) -> None:
    """
    Запрет удаления DJ
    :param client:
    :param user:
    :param dj:
    :return:
    """
    headers = create_auth_header(user["username"])
    user_response = await client.delete(f'/djs/{dj["slug"]}', headers=headers)
    guest_response = await client.delete(f'/djs/{dj["slug"]}')

    assert user_response.status_code == status.HTTP_403_FORBIDDEN
    assert guest_response.status_code == status.HTTP_401_UNAUTHORIZED
    assert await dj_crud.find(id_=dj["id"])


@pytest.mark.asyncio()
async def test_delete_group(
    client: AsyncClient,
    admin: Mapping,
    group: Mapping,
) -> None:
    """
    Удаление группы
    :param client:
    :param admin:
    :param group:
    :return:
    """
    headers = create_auth_header(admin["username"])
    response = await client.delete(f'/djs/{group["slug"]}', headers=headers)
    group_members = await dj_crud.get_groups_members(ids=[group["id"]])

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert await dj_crud.find(id_=group["id"]) is None
    assert not len(group_members)


@pytest.mark.asyncio()
async def test_get_list(
    client: AsyncClient,
    group: Mapping,
    dj: Mapping,
) -> None:
    """
    Получение списка DJs
    :param client:
    :param dj:
    :return:
    """
    response = await client.get("/djs")
    data = response.json()
    count = await dj_crud.count()

    assert response.status_code == status.HTTP_200_OK
    assert len(data) == count
    assert response.headers["X-Pagination-Total-Count"] == str(count)


@pytest.mark.asyncio()
async def test_get(client: AsyncClient, group: Mapping, dj: Mapping) -> None:
    """
    Получение DJ
    :param client:
    :param group:
    :return:
    """
    response = await client.get(f'/djs/{group["slug"]}')
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["id"] == group["id"]
    assert data["group_members"] == [dj["slug"]]


@pytest.mark.asyncio()
async def test_patch(client: AsyncClient, dj: Mapping, admin: Mapping) -> None:
    """
    Изменение DJ
    :param client:
    :param dj:
    :return:
    """
    auth_headers = create_auth_header(admin["username"])
    new_data = {
        "name": f'new{dj["name"]}',
        "real_name": f'new{dj["real_name"]}',
    }
    response = await client.patch(
        f'/djs/{dj["slug"]}',
        headers=auth_headers,
        json=new_data,
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["slug"] == dj["slug"]
    assert data["name"] == new_data["name"]
    db_dj = await dj_crud.find(name=new_data["name"])
    assert db_dj["slug"] == dj["slug"]


@pytest.mark.asyncio()
async def test_prohibit_patch(
    client: AsyncClient,
    dj: Mapping,
    user: Mapping,
) -> None:
    """
    Проверка прав на изменение DJ
    :param client:
    :param dj:
    :param user:
    :return:
    """
    new_data = {"name": "New name"}
    auth_headers = create_auth_header(user["username"])
    response = await client.patch(
        f'/djs/{dj["slug"]}',
        headers=auth_headers,
        json=new_data,
    )
    db_dj = await dj_crud.find(dj["id"])

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert db_dj["name"] == dj["name"]


@pytest.mark.asyncio()
async def test_patch_group(
    client: AsyncClient,
    dj: Mapping,
    group: Mapping,
    admin: Mapping,
) -> None:
    """
    Изменение членов группы
    :param client:
    :param dj:
    :param group:
    :param admin:
    :return:
    """
    auth_headers = create_auth_header(admin["username"])
    response = await client.patch(
        f'/djs/{group["slug"]}',
        headers=auth_headers,
        json={"is_group": False},
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["group_members"] == []
    assert not data["is_group"]
    assert not await dj_crud.get_groups_members([group["id"]])

    new_data = {"is_group": True, "group_members": [dj["id"]]}
    response = await client.patch(
        f'/djs/{group["slug"]}',
        headers=auth_headers,
        json=new_data,
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["group_members"] == [dj["slug"]]
    assert data["is_group"]
    assert await dj_crud.get_groups_members([group["id"]])

    new_data = {"group_members": []}
    response = await client.patch(
        f'/djs/{group["slug"]}',
        headers=auth_headers,
        json=new_data,
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert not data["group_members"]
    assert data["is_group"]
    assert not await dj_crud.get_groups_members([group["id"]])
