from starlette import status
from starlette.testclient import TestClient

from tests.helpers import create_auth_header


####################################
# DELETE /channels/{slug}
####################################
def test_delete_channel(
        client: TestClient,
        channel_to_be_deleted: dict,
        admin: dict,
):
    auth_headers = create_auth_header(admin['username'])
    response = client.delete(
        f'/channels/{channel_to_be_deleted["slug"]}',
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_channel_without_auth(
        client: TestClient,
        channel_to_be_deleted: dict
):
    response = client.delete(f'/channels/{channel_to_be_deleted["slug"]}')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_channel_by_user(
        client: TestClient,
        channel_to_be_deleted: dict,
        user: dict,
):
    auth_headers = create_auth_header(user['username'])
    response = client.delete(
        f'/channels/{channel_to_be_deleted["slug"]}',
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_channel_not_found(
        client: TestClient,
        channel_to_be_deleted: dict,
        admin: dict,
):
    auth_headers = create_auth_header(admin['username'])
    response = client.delete(
        f'/channels/{channel_to_be_deleted["slug"]}notfound',
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
