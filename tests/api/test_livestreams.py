from datetime import date, timedelta
from typing import Mapping, cast

import pytest
from httpx import AsyncClient
from starlette import status

from app.crud import livestream as livestream_crud
from app.schemas.livestreams import LiveStream, CreateLiveStream
from tests.helpers import create_auth_header


@pytest.mark.asyncio
async def test_create_livestream(
        client: AsyncClient,
        livestream_data: CreateLiveStream,
        admin: Mapping,
) -> None:
    """
    Создание трансляции
    :param client:
    :param livestream_data:
    :param admin:
    :return:
    """
    headers = create_auth_header(admin['username'])
    response = await client.post(
        '/livestreams',
        content=livestream_data.json(),
        headers=headers,
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert LiveStream.validate(data)
    assert await livestream_crud.find_one(data['id'])


@pytest.mark.asyncio
async def test_prevent_duplicate_livestreams(
        client: AsyncClient,
        livestream_data: CreateLiveStream,
        livestream: Mapping,
        admin: Mapping,
) -> None:
    """Проверка уникальности прямых трансляций"""
    headers = create_auth_header(admin['username'])
    response = await client.post(
        '/livestreams',
        content=livestream_data.json(),
        headers=headers,
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert await livestream_crud.find_one(slug=livestream['slug'])


@pytest.mark.asyncio
async def test_disallow_creation_livestream_without_privileges(
        client: AsyncClient,
        livestream_data: CreateLiveStream,
        user: Mapping,
) -> None:
    """
    Проверка прав на добавление
    :param client:
    :param livestream_data:
    :param user:
    :return:
    """
    headers = create_auth_header(user['username'])
    response = await client.post(
        '/livestreams',
        content=livestream_data.json(),
        headers=headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not await livestream_crud.find_one(title=livestream_data.title)

    response = await client.post(
        '/livestreams',
        content=livestream_data.json(),
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert not await livestream_crud.find_one(title=livestream_data.title)


@pytest.mark.asyncio
async def test_get_livestreams(
        client: AsyncClient,
        livestream: Mapping,
        livestream_in_a_month: Mapping,
) -> None:
    """
    Получение списка трансляций
    :param client:
    :param livestream:
    :param livestream_in_a_month:
    :return:
    """
    response = await client.get('/livestreams')

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data[0]['title'] == livestream['title']
    assert len(data) == 1


@pytest.mark.asyncio
async def test_period_excess_error(
        client: AsyncClient,
) -> None:
    """
    Валидация дат периода выборки
    :param client:
    :return:
    """
    start_date = date.today() - timedelta(days=20)
    end_date = start_date + timedelta(days=46)
    response = await client.get(
        '/livestreams',
        params={
            'start': start_date.isoformat(),
            'end': end_date.isoformat(),
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()['detail'] == 'Период не может превышать 45 дней'


@pytest.mark.asyncio
async def test_get_livestream(
        client: AsyncClient,
        livestream: Mapping,
) -> None:
    """
    Получить трансляцию
    :param client:
    :param livestream:
    :return:
    """
    response = await client.get(
        f'/livestreams/{livestream["id"]}:{livestream["slug"]}',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['title'] == livestream['title']


@pytest.mark.asyncio
async def test_remove_livestream(
        client: AsyncClient,
        livestream: Mapping,
        admin: Mapping,
) -> None:
    """
    Удалить трансляцию
    :param client:
    :param livestream:
    :param admin:
    :return:
    """
    headers = create_auth_header(admin['username'])
    response = await client.delete(
        f'/livestreams/{livestream["id"]}:{livestream["slug"]}',
        headers=headers,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not await livestream_crud.find_one(livestream['id'])


@pytest.mark.asyncio
async def test_removal_without_privileges(
        client: AsyncClient,
        livestream: Mapping,
        user: Mapping,
) -> None:
    """
    Проверка прав на удаление
    :param client:
    :param livestream:
    :param user:
    :return:
    """
    response = await client.delete(
        f'/livestreams/{livestream["id"]}:{livestream["slug"]}',
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert await livestream_crud.find_one(livestream['id'])

    headers = create_auth_header(user['username'])
    response = await client.delete(
        f'/livestreams/{livestream["id"]}:{livestream["slug"]}',
        headers=headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert await livestream_crud.find_one(livestream['id'])


@pytest.mark.asyncio
async def test_update_livestream(
        client: AsyncClient,
        livestream: Mapping,
        admin: Mapping,
) -> None:
    """
    Обноавление трансляции
    :param client:
    :param livestream:
    :param admin:
    :return:
    """
    headers = create_auth_header(admin['username'])
    stream = dict(livestream)
    stream['title'] = 'Новое название'
    stream['start_time'] = stream['start_time'].isoformat()
    stream['end_time'] = None
    response = await client.put(
        f'/livestreams/{livestream["id"]}:{livestream["slug"]}',
        headers=headers,
        json=stream,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert LiveStream.validate(data)
    db_stream = cast(Mapping, await livestream_crud.find_one(livestream['id']))
    assert db_stream['slug'] == data['slug']
    assert db_stream['title'] == stream['title']


@pytest.mark.asyncio
async def test_update_without_privileges(
        client: AsyncClient,
        livestream: Mapping,
        user: Mapping,
) -> None:
    """
    Проверка прав на обновление
    :param client:
    :param livestream:
    :param user:
    :return:
    """
    headers = create_auth_header(user['username'])
    response = await client.put(
        f'/livestreams/{livestream["id"]}:{livestream["slug"]}',
        headers=headers,
        json={'title': 'Новый заголовок'},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    db_stream = cast(Mapping, await livestream_crud.find_one(livestream['id']))
    assert db_stream['title'] == livestream['title']

    response = await client.put(
        f'/livestreams/{livestream["id"]}:{livestream["slug"]}',
        json={'title': 'Новый заголовок'},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    db_stream = cast(Mapping, await livestream_crud.find_one(livestream['id']))
    assert db_stream['title'] == livestream['title']
