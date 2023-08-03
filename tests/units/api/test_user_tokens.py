import jwt
import pytest
from faker import Faker
from fastapi import status
from httpx import AsyncClient
from pytest_mock import MockerFixture
from typing_extensions import Self

from app.internal.controller.http.v1.requests.user_tokens import (
    CreateAPITokenRequest,
)
from app.internal.entity.settings import settings
from app.internal.entity.user import UserToken
from app.internal.usecase.exceptions.user_tokens import UserTokenNotFoundError


@pytest.fixture()
def request_data(faker: Faker) -> CreateAPITokenRequest:
    return CreateAPITokenRequest(
        name=faker.word(),
    )


@pytest.fixture()
def user_token(
    request_data: CreateAPITokenRequest,
    faker: Faker,
) -> UserToken:
    return UserToken(
        name=request_data.name,
        id=1,
        created_at=faker.past_datetime(),
    )


class TestCreateAPIToken:
    @pytest.mark.usefixtures("_mock_current_admin")
    async def test_create_token(
        self: Self,
        client: AsyncClient,
        request_data: CreateAPITokenRequest,
        user_token: UserToken,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.user_tokens.CreateUserTokenUseCase.execute",
            return_value=user_token,
        )
        response = await client.post(
            "/users/tokens",
            json=request_data.model_dump(),
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.usefixtures("_mock_current_admin")
    async def test_create_token_without_expired_at(
        self: Self,
        client: AsyncClient,
        request_data: CreateAPITokenRequest,
        user_token: UserToken,
        mocker: MockerFixture,
    ) -> None:
        request_data.expired_at = None
        user_token.expired_at = None

        mocked = mocker.patch(
            "app.internal.usecase.user_tokens.CreateUserTokenUseCase.execute",
            return_value=user_token,
        )
        response = await client.post(
            "/users/tokens",
            json=request_data.model_dump(),
        )
        data = response.json()

        payload = jwt.decode(
            data["token"],
            settings.secret_key,
            algorithms=["HS256"],
        )

        assert "exp" not in payload or payload["exp"] is None

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.usefixtures("_mock_current_user")
    async def test_without_permissions(
        self: Self,
        client: AsyncClient,
        request_data: CreateAPITokenRequest,
        mocker: MockerFixture,
    ) -> None:
        response = await client.post(
            "/users/tokens",
            json=request_data.model_dump(),
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetAllUserTokens:
    @pytest.mark.usefixtures("_mock_current_admin")
    async def test_get_all_tokens(
        self: Self,
        client: AsyncClient,
        user_token: UserToken,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.user_tokens.GetAllUserTokensUseCase.execute",
            return_value=[user_token],
        )
        response = await client.get("/users/tokens")

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.usefixtures("_mock_current_user")
    async def test_without_permissions(
        self: Self,
        client: AsyncClient,
    ) -> None:
        response = await client.get("/users/tokens")

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestRevokeAPIToken:
    @pytest.mark.usefixtures("_mock_current_admin")
    async def test_revoke_token(
        self: Self,
        client: AsyncClient,
        user_token: UserToken,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.user_tokens.RevokeUserTokenUseCase.execute",
            return_value=None,
        )
        response = await client.delete(
            f"/users/tokens/{user_token.id}",
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.usefixtures("_mock_current_admin")
    async def test_revoke_token_not_found(
        self: Self,
        client: AsyncClient,
        user_token: UserToken,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.user_tokens.RevokeUserTokenUseCase.execute",
            side_effect=UserTokenNotFoundError,
        )
        response = await client.delete(
            f"/users/tokens/{user_token.id}",
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.usefixtures("_mock_current_user")
    async def test_without_permissions(
        self: Self,
        client: AsyncClient,
        user_token: UserToken,
    ) -> None:
        response = await client.delete(
            f"/users/tokens/{user_token.id}",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
