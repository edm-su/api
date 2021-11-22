from typing import Mapping

import pytest
from httpx import AsyncClient
from starlette import status

from app.crud import token as token_crud, livestream as livestream_crud
from app.schemas.user import CreateUser, UserPassword, User, MyUser, Token
from tests.helpers import create_auth_header


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient) -> None:
    new_user = CreateUser(
        password='testpassword',
        password_confirm='testpassword',
        username='TestUser',
        email='testuser@example.com',
    )
    response = await client.post('/users', json=new_user.dict())

    assert response.status_code == status.HTTP_200_OK
    assert MyUser.validate(response.json())
    assert response.json()['is_admin'] is False


@pytest.mark.asyncio
async def test_activate_user(
        client: AsyncClient,
        non_activated_user: Mapping,
) -> None:
    url = f'/users/activate/{non_activated_user["activation_code"]}'
    response = await client.post(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_login(client: AsyncClient, admin: Mapping) -> None:
    response = await client.post(
        '/users/token',
        data={
            'username': admin['username'],
            'password': 'password',
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert Token.validate(response.json())


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, admin: Mapping) -> None:
    response = await client.get(
        '/users/me',
        headers=create_auth_header(admin['username']),
    )

    assert response.status_code == status.HTTP_200_OK
    assert MyUser.validate(response.json())


@pytest.mark.asyncio
async def test_request_recovery_user(
        client: AsyncClient,
        admin: Mapping,
) -> None:
    response = await client.post(f'/users/password-recovery/{admin["email"]}')

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_change_password(client: AsyncClient, admin: Mapping) -> None:
    data = {
        'new_password': {
            'password': 'newpassword',
            'password_confirm': 'newpassword',
        },
        'old_password': 'password',
    }
    response = await client.put(
        '/users/password',
        headers=create_auth_header(admin['username']),
        json=data,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_reset_password(
        client: AsyncClient,
        recovered_user_code: str,
) -> None:
    data = UserPassword(password='newpassword', password_confirm='newpassword')
    url = f'/users/reset-password/{recovered_user_code}'
    response = await client.put(url, json=data.dict())

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_read_user(client: AsyncClient, admin: Mapping) -> None:
    response = await client.get(f'/users/{admin["id"]}')

    assert response.status_code == status.HTTP_200_OK
    assert User.validate(response.json())


########################################
# POST /users/token
########################################
@pytest.mark.asyncio
async def test_create_api_token(
        client: AsyncClient,
        admin: Mapping,
        user: Mapping,
) -> None:
    headers = create_auth_header(admin['username'])
    data = {'name': 'New token'}
    response = await client.post(
        '/users/api_token',
        headers=headers,
        json=data,
    )
    response_data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert await token_crud.find_token(response_data['token'])

    headers = create_auth_header(user['username'])
    response = await client.post(
        '/users/api_token',
        headers=headers,
        json=data,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = await client.post(
        '/users/api_token',
        json=data,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


########################################
# Token authentication
########################################
@pytest.mark.asyncio
async def test_api_token_authentication(
        client: AsyncClient,
        api_token: str,
        livestream_data: dict,
) -> None:
    headers = {'Authorization': f'Token {api_token}'}
    response = await client.post(
        '/livestreams',
        json=livestream_data,
        headers=headers,
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert await livestream_crud.find_one(data['id'])

    headers = {'Authorization': f'Token bad{api_token}'}
    response = await client.post(
        '/livestreams',
        json=livestream_data,
        headers=headers,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
