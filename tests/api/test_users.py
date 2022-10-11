from typing import Mapping

import pytest
from httpx import AsyncClient
from starlette import status

from app.crud import livestream as livestream_crud
from app.crud import token as token_crud
from app.schemas import user as user_schemas
from app.schemas.livestreams import CreateLiveStream
from tests.helpers import create_auth_header


@pytest.mark.asyncio
async def test_create_user(
    client: AsyncClient, user_data: user_schemas.CreateUser
) -> None:
    """
    Регистрация
    :param client:
    :return:
    """
    new_user = user_schemas.CreateUser(
        password=user_data.password,
        password_confirm=user_data.password,
        username=user_data.username,
        email=user_data.email,
    )
    response = await client.post("/users", json=new_user.dict())

    assert response.status_code == status.HTTP_200_OK
    assert user_schemas.MyUser.validate(response.json())
    assert response.json()["is_admin"] is False


@pytest.mark.asyncio
async def test_activate_user(
    client: AsyncClient,
    non_activated_user: Mapping,
) -> None:
    """
    Подтверждение пользователя
    :param client:
    :param non_activated_user:
    :return:
    """
    url = f'/users/activate/{non_activated_user["activation_code"]}'
    response = await client.post(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_login(
    client: AsyncClient,
    admin: Mapping,
    user_data: user_schemas.CreateUser,
) -> None:
    """
    Авторизация
    :param client:
    :param admin:
    :param user_data:
    :return:
    """
    response = await client.post(
        "/users/token",
        data={
            "username": user_data.username,
            "password": user_data.password,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert user_schemas.Token.validate(response.json())


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, admin: Mapping) -> None:
    """
    Получение информации о пользователе
    :param client:
    :param admin:
    :return:
    """
    response = await client.get(
        "/users/me",
        headers=create_auth_header(admin["username"]),
    )

    assert response.status_code == status.HTTP_200_OK
    assert user_schemas.MyUser.validate(response.json())


@pytest.mark.asyncio
async def test_request_recovery_user(
    client: AsyncClient,
    admin: Mapping,
) -> None:
    """
    Запрос восстановления пользователя
    :param client:
    :param admin:
    :return:
    """
    response = await client.post(f'/users/password-recovery/{admin["email"]}')

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_change_password(
    client: AsyncClient,
    admin: Mapping,
    user_data: user_schemas.CreateUser,
) -> None:
    """
    Изменение пароля
    :param client:
    :param admin:
    :return:
    """
    data = {
        "new_password": {
            "password": "new-password",
            "password_confirm": "new-password",
        },
        "old_password": user_data.password,
    }
    response = await client.put(
        "/users/password",
        headers=create_auth_header(admin["username"]),
        json=data,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_reset_password(
    client: AsyncClient,
    recovered_user_code: str,
) -> None:
    """
    Сброс пароля
    :param client:
    :param recovered_user_code:
    :return:
    """
    password = "new-password"
    data = user_schemas.UserPassword(
        password=password,
        password_confirm=password,
    )
    url = f"/users/reset-password/{recovered_user_code}"
    response = await client.put(url, json=data.dict())

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_read_user(client: AsyncClient, admin: Mapping) -> None:
    """
    Информация о пользователе
    :param client:
    :param admin:
    :return:
    """
    response = await client.get(f'/users/{admin["id"]}')

    assert response.status_code == status.HTTP_200_OK
    assert user_schemas.User.validate(response.json())


@pytest.mark.asyncio
async def test_create_api_token(
    client: AsyncClient,
    admin: Mapping,
) -> None:
    """
    Создание api токена
    :param client:
    :param admin:
    :return:
    """
    headers = create_auth_header(admin["username"])
    data = {"name": "New token"}
    response = await client.post(
        "/users/api_token",
        headers=headers,
        json=data,
    )
    response_data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert await token_crud.find_token(response_data["token"])


@pytest.mark.asyncio
async def test_create_api_token_without_auth(
    client: AsyncClient,
    user: Mapping,
) -> None:
    """
    Проверка прав на создание api токена
    :param client:
    :param user:
    :return:
    """
    headers = create_auth_header(user["username"])
    data = {"name": "New token"}
    response = await client.post(
        "/users/api_token",
        headers=headers,
        json=data,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = await client.post(
        "/users/api_token",
        json=data,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_api_token_authentication(
    client: AsyncClient,
    api_token: str,
    livestream_data: CreateLiveStream,
) -> None:
    """
    Авторизация с использованием api токена
    :param client:
    :param api_token:
    :param livestream_data:
    :return:
    """
    headers = {"Authorization": f"Token {api_token}"}
    response = await client.post(
        "/livestreams",
        content=livestream_data.json(),
        headers=headers,
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert await livestream_crud.find_one(data["id"])

    headers = {"Authorization": f"Token bad{api_token}"}
    response = await client.post(
        "/livestreams",
        content=livestream_data.json(),
        headers=headers,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
