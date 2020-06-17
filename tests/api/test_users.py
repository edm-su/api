from starlette import status
from starlette.testclient import TestClient

from app.schemas.user import CreateUser, UserPassword, User, MyUser, Token
from tests.helpers import create_auth_header


def test_create_user(client: TestClient):
    new_user = CreateUser(
        password='testpassword',
        password_confirm='testpassword',
        username='TestUser',
        email='testuser@example.com',
    )
    response = client.post('/users/', data=new_user.json())

    assert response.status_code == status.HTTP_200_OK
    assert MyUser.validate(response.json())
    assert response.json()['is_admin'] == False


def test_activate_user(client, non_activated_user):
    url = f'/users/activate/{non_activated_user["activation_code"]}'
    response = client.post(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_login(client: TestClient, admin: dict):
    response = client.post(
        '/users/token',
        data={
            'username': admin['username'],
            'password': 'password',
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert Token.validate(response.json())


def test_get_current_user(client: TestClient, admin: dict):
    response = client.get(
        '/users/me',
        headers=create_auth_header(admin['username']),
    )

    assert response.status_code == status.HTTP_200_OK
    assert MyUser.validate(response.json())


def test_request_recovery_user(client: TestClient, admin: dict):
    response = client.post(f'/users/password-recovery/{admin["email"]}')

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_change_password(client: TestClient, admin: dict):
    data = {
        'new_password': {
            'password': 'newpassword',
            'password_confirm': 'newpassword',
        },
        'old_password': 'password',
    }
    response = client.put(
        '/users/password',
        headers=create_auth_header(admin['username']),
        json=data,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_reset_password(client: TestClient, recovered_user_code: str):
    data = UserPassword(password='newpassword', password_confirm='newpassword')
    url = f'/users/reset-password/{recovered_user_code}'
    response = client.put(url, data=data.json())

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_read_user(client: TestClient, admin: dict):
    response = client.get(f'/users/{admin["username"]}')

    assert response.status_code == status.HTTP_200_OK
    assert User.validate(response.json())
