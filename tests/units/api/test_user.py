from datetime import datetime, timedelta

import pytest
from faker import Faker
from fastapi import status
from httpx import AsyncClient
from pytest_mock import MockerFixture
from typing_extensions import Self

from app.internal.controller.http.v1.requests.user import (
    ActivateUserRequest,
    ChangePasswordRequest,
    PasswordResetRequest,
    SignInRequest,
    SignUpRequest,
)
from app.internal.entity.user import ResetPasswordDto, User
from app.internal.usecase.exceptions.user import (
    UserAlreadyExistsError,
    UserError,
    UserIsBannedError,
    UserIsNotActivatedError,
    UserNotFoundError,
    WrongActivationCodeError,
    WrongPasswordOrEmailError,
)


class TestSignUp:
    @pytest.fixture()
    def data(
        self: Self,
        user: User,
    ) -> SignUpRequest:
        return SignUpRequest(
            username=user.username,
            email=user.email,
            password="password",
        )

    async def test_sign_up(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
        user: User,
        data: SignUpRequest,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.user.CreateUserUseCase.execute",
            return_value=user,
        )
        response = await client.post(
            "/users",
            content=data.json(),
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_201_CREATED

    async def test_user_already_exists(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
        data: SignUpRequest,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.user.CreateUserUseCase.execute",
            side_effect=UserAlreadyExistsError("email"),
        )
        response = await client.post(
            "/users",
            content=data.json(),
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_409_CONFLICT


class TestActivateUser:
    @pytest.fixture()
    def data(
        self: Self,
        faker: Faker,
    ) -> ActivateUserRequest:
        return ActivateUserRequest(
            id=1,
            activation_code=(
                faker.pystr(
                    min_chars=10,
                    max_chars=10,
                )
            ).upper(),
        )

    async def test_activate_user(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
        data: ActivateUserRequest,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.user.ActivateUserUseCase.execute",
        )
        response = await client.post(
            "/users/activate",
            content=data.json(),
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_bad_code(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
        data: ActivateUserRequest,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.user.ActivateUserUseCase.execute",
            side_effect=WrongActivationCodeError,
        )
        response = await client.post(
            "/users/activate",
            content=data.json(),
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestMe:
    @pytest.mark.usefixtures("_mock_current_user")
    async def test_me(
        self: Self,
        client: AsyncClient,
        user: User,
    ) -> None:
        response = await client.get("/users/me")
        response_data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert response_data["id"] == user.id

    async def test_not_authenticated(
        self: Self,
        client: AsyncClient,
    ) -> None:
        response = await client.get("/users/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestResetPassword:
    @pytest.fixture()
    def data(
        self: Self,
        user: User,
    ) -> PasswordResetRequest:
        return PasswordResetRequest(
            email=user.email,
        )

    async def test_reset_password(
        self: Self,
        client: AsyncClient,
        data: PasswordResetRequest,
        mocker: MockerFixture,
        user: User,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.user.ResetPasswordUseCase.execute",
            return_value=ResetPasswordDto(
                id=user.id,
                code="AAAAAAAAAA",
                expires=datetime.now() + timedelta(hours=24),
            ),
        )
        mocked_send_email = mocker.patch(
            "fastapi.BackgroundTasks.add_task",
        )
        response = await client.post(
            "/users/password/reset",
            content=data.json(),
        )

        mocked.assert_awaited_once()
        mocked_send_email.assert_called_once()
        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_user_not_found(
        self: Self,
        client: AsyncClient,
        data: PasswordResetRequest,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.user.ResetPasswordUseCase.execute",
            side_effect=UserNotFoundError,
        )
        response = await client.post(
            "/users/password/reset",
            content=data.json(),
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_bad_error(
        self: Self,
        client: AsyncClient,
        data: PasswordResetRequest,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.user.ResetPasswordUseCase.execute",
            side_effect=UserError,
        )
        response = await client.post(
            "/users/password/reset",
            content=data.json(),
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestChangePassword:
    @pytest.fixture()
    def data(
        self: Self,
        user: User,
    ) -> ChangePasswordRequest:
        return ChangePasswordRequest(
            user_id=user.id,
            old_password="password",
            new_password="new_password",
        )

    async def test_change_password(
        self: Self,
        client: AsyncClient,
        data: ChangePasswordRequest,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.user.ChangePasswordUseCase.execute",
            return_value=True,
        )
        response = await client.put(
            "/users/password",
            content=data.json(),
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_change_by_reset_code(
        self: Self,
        client: AsyncClient,
        data: ChangePasswordRequest,
        mocker: MockerFixture,
    ) -> None:
        del data.old_password
        data.reset_code = "AAAAAAAAAA"
        mocked = mocker.patch(
            "app.internal.usecase.user.ChangePasswordByResetCodeUseCase.execute",
            return_value=True,
        )
        response = await client.put(
            "/users/password",
            content=data.json(),
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_without_old_password_or_reset_code(
        self: Self,
        client: AsyncClient,
        data: ChangePasswordRequest,
    ) -> None:
        del data.old_password
        response = await client.put(
            "/users/password",
            content=data.json(),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestSignIn:
    @pytest.fixture()
    def data(
        self: Self,
        user: User,
    ) -> SignInRequest:
        return SignInRequest(
            email=user.email,
            password="password",
        )

    async def test_sign_in(
        self: Self,
        client: AsyncClient,
        data: SignInRequest,
        mocker: MockerFixture,
        user: User,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.user.SignInUseCase.execute",
            return_value=user,
        )
        response = await client.post(
            "/users/sign-in",
            content=data.json(),
        )
        response_data = response.json()

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_200_OK
        assert response_data["refresh_token"] is None

    async def test_remember_me(
        self: Self,
        client: AsyncClient,
        data: SignInRequest,
        mocker: MockerFixture,
        user: User,
    ) -> None:
        data.remember_me = True
        mocked = mocker.patch(
            "app.internal.usecase.user.SignInUseCase.execute",
            return_value=user,
        )
        response = await client.post(
            "/users/sign-in",
            content=data.json(),
        )
        response_data = response.json()

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_200_OK
        assert response_data["refresh_token"]

    async def test_wrong_password(
        self: Self,
        client: AsyncClient,
        data: SignInRequest,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.user.SignInUseCase.execute",
            side_effect=WrongPasswordOrEmailError,
        )
        response = await client.post(
            "/users/sign-in",
            content=data.json(),
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_user_is_banned(
        self: Self,
        client: AsyncClient,
        data: SignInRequest,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.user.SignInUseCase.execute",
            side_effect=UserIsBannedError,
        )
        response = await client.post(
            "/users/sign-in",
            content=data.json(),
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_user_is_not_active(
        self: Self,
        client: AsyncClient,
        data: SignInRequest,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.user.SignInUseCase.execute",
            side_effect=UserIsNotActivatedError,
        )
        response = await client.post(
            "/users/sign-in",
            content=data.json(),
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
