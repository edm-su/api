from collections.abc import Mapping

from httpx import AsyncClient
from starlette import status

from tests.helpers import create_auth_header


async def test_create_token(
    client: AsyncClient,
    admin: Mapping,
) -> None:
    """
    Тест создание токена
    :param client:
    :param admin:
    :return:
    """
    auth_headers = create_auth_header(admin["username"])
    response = await client.post(
        "/users/api_token",
        json={"name": "test_token"},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["token"] is not None
