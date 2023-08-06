import pytest
from faker import Faker
from fastapi import status
from httpx import AsyncClient
from pytest_mock import MockerFixture
from typing_extensions import Self

from app.internal.controller.http.v1.dependencies.auth import (
    get_refresh_token_data_and_user,
)
from app.internal.controller.http.v1.requests.user import (
    ActivateUserRequest,
    ChangePasswordRequest,
    CompleteResetPasswordRequest,
    PasswordResetRequest,
    SignInRequest,
    SignUpRequest,
)
from app.internal.entity.user import User
from app.internal.usecase.exceptions.user import (
    UserAlreadyExistsError,
    UserError,
    UserIsBannedError,
    UserIsNotActivatedError,
    UserNotFoundError,
    WrongActivationCodeError,
    WrongPasswordError,
    WrongPasswordOrEmailError,
)
from app.main import app


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
            content=data.model_dump_json(),
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
            content=data.model_dump_json(),
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
            content=data.model_dump_json(),
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
            content=data.model_dump_json(),
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
            return_value=None,
        )
        response = await client.post(
            "/users/password/reset",
            content=data.model_dump_json(),
        )

        mocked.assert_awaited_once()
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
            content=data.model_dump_json(),
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
            content=data.model_dump_json(),
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestCompleteResetPassword:
    @pytest.fixture()
    def data(
        self: Self,
        user: User,
    ) -> CompleteResetPasswordRequest:
        return CompleteResetPasswordRequest(
            user_id=user.id,
            code="AAAAAAAAAA",
            new_password="new_password",
        )

    async def test_complete_reset_password(
        self: Self,
        client: AsyncClient,
        data: CompleteResetPasswordRequest,
        mocker: MockerFixture,
        user: User,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.user.ChangePasswordByResetCodeUseCase.execute",
            return_value=None,
        )
        response = await client.put(
            "/users/password/reset",
            content=data.model_dump_json(),
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        mocked.assert_awaited_once()

    async def test_bad_user_id(
        self: Self,
        client: AsyncClient,
        data: CompleteResetPasswordRequest,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.user.ChangePasswordByResetCodeUseCase.execute",
            side_effect=UserNotFoundError,
        )
        response = await client.put(
            "/users/password/reset",
            content=data.model_dump_json(),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        mocked.assert_awaited_once()


class TestChangePassword:
    @pytest.fixture()
    def data(
        self: Self,
        user: User,
    ) -> ChangePasswordRequest:
        return ChangePasswordRequest(
            old_password="password",
            new_password="new_password",
        )

    @pytest.mark.usefixtures("_mock_current_user")
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
            content=data.model_dump_json(),
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_change_password_without_auth(
        self: Self,
        client: AsyncClient,
        data: ChangePasswordRequest,
    ) -> None:
        response = await client.put(
            "/users/password",
            content=data.model_dump_json(),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.usefixtures("_mock_current_user")
    async def test_bad_user_id(
        self: Self,
        client: AsyncClient,
        data: ChangePasswordRequest,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.user.ChangePasswordUseCase.execute",
            side_effect=UserNotFoundError,
        )
        response = await client.put(
            "/users/password",
            content=data.model_dump_json(),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        mocked.assert_awaited_once()

    @pytest.mark.usefixtures("_mock_current_user")
    async def test_wrong_old_password(
        self: Self,
        client: AsyncClient,
        data: ChangePasswordRequest,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.user.ChangePasswordUseCase.execute",
            side_effect=WrongPasswordError,
        )
        response = await client.put(
            "/users/password",
            content=data.model_dump_json(),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        mocked.assert_awaited_once()


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
            content=data.model_dump_json(),
        )
        response_data = response.json()

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_200_OK
        assert response_data["refresh_token"] is None
        assert response_data["access_token"] != "**********"

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
            content=data.model_dump_json(),
        )
        response_data = response.json()

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_200_OK
        assert response_data["refresh_token"]
        assert response_data["access_token"] != "**********"

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
            content=data.model_dump_json(),
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
            content=data.model_dump_json(),
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
            content=data.model_dump_json(),
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRefreshToken:
    @pytest.fixture()
    def _mock_current_user(
        self: Self,
        user: User,
    ) -> None:
        app.dependency_overrides[
            get_refresh_token_data_and_user
        ] = lambda: user

    @pytest.mark.usefixtures("_mock_current_user")
    async def test_refresh_token(
        self: Self,
        client: AsyncClient,
    ) -> None:
        response = await client.post(
            "/users/token",
            params={
                "refresh_token": "**********",
                "grant_type": "refresh_token",
            },
        )

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.usefixtures("_mock_current_user")
    async def test_broken_grant_type(
        self: Self,
        client: AsyncClient,
    ) -> None:
        response = await client.post(
            "/users/token",
            params={
                "refresh_token": "**********",
                "grant_type": "refresh_token1",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
