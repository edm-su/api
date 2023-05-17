from datetime import timezone
from unittest.mock import AsyncMock

import pytest
from faker import Faker
from pydantic import SecretStr
from pytest_mock import MockerFixture
from typing_extensions import Self

from app.internal.entity.user import (
    ActivateUserDto,
    ChangePasswordByResetCodeDto,
    ChangePasswordDto,
    NewUserDto,
    User,
)
from app.internal.usecase.exceptions.user import (
    UserAlreadyExistsError,
    UserNotFoundError,
    WrongActivationCodeError,
    WrongPasswordError,
    WrongResetCodeError,
)
from app.internal.usecase.repository.user import AbstractUserRepository
from app.internal.usecase.user import (
    ActivateUserUseCase,
    ChangePasswordByResetCodeUseCase,
    ChangePasswordUseCase,
    CreateUserUseCase,
    GetUserByIdUseCase,
    GetUserByUsernameUseCase,
    ResetPasswordUseCase,
)


@pytest.fixture()
def repository(mocker: MockerFixture) -> AbstractUserRepository:
    return AsyncMock(repr=AbstractUserRepository)


@pytest.fixture()
def user(faker: Faker) -> User:
    return User(
        id=faker.random_int(),
        username=faker.user_name(),
        email=faker.email(),
        created=faker.past_datetime(tzinfo=timezone.utc),
    )


@pytest.fixture()
def my_user(faker: Faker) -> User:
    return User(
        id=faker.random_int(),
        username=faker.user_name(),
        is_admin=False,
        email=faker.email(),
        created=faker.past_datetime(tzinfo=timezone.utc),
    )


@pytest.fixture()
def new_user(faker: Faker) -> NewUserDto:
    return NewUserDto(
        email=faker.email(),
        password=faker.password(),
        username=faker.user_name(),
    )


class TestCreateUserUseCase:
    @pytest.fixture(autouse=True)
    def _mock(
        self: Self,
        user: User,
        repository: AsyncMock,
    ) -> None:
        repository.get_by_email.return_value = None
        repository.get_by_username.return_value = None
        repository.create.return_value = user

    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> CreateUserUseCase:
        return CreateUserUseCase(repository)

    async def test_create_user(
        self: Self,
        usecase: AsyncMock,
        new_user: NewUserDto,
        user: User,
    ) -> None:
        assert await usecase.execute(new_user) == user

        usecase.repository.get_by_email.assert_awaited_once_with(
            new_user.email,
        )
        usecase.repository.get_by_username.assert_awaited_once_with(
            new_user.username,
        )
        usecase.repository.create.assert_awaited_once()

    @pytest.mark.parametrize("get_by", ["email", "username"])
    async def test_create_already_exists_user(
        self: Self,
        usecase: AsyncMock,
        new_user: NewUserDto,
        user: User,
        repository: AsyncMock,
        get_by: str,
    ) -> None:
        if get_by == "email":
            repository_method = repository.get_by_email
        else:
            repository_method = repository.get_by_username
        repository_method.return_value = user

        with pytest.raises(UserAlreadyExistsError):
            await usecase.execute(new_user)

        usecase.repository.create.assert_not_awaited()


class TestActivateUserUseCase:
    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> ActivateUserUseCase:
        return ActivateUserUseCase(repository)

    @pytest.fixture()
    def activate_user(
        self: Self,
        user: User,
        faker: Faker,
    ) -> ActivateUserDto:
        return ActivateUserDto(
            id=user.id,
            activation_code=faker.password(),
        )

    async def test_activate_user(
        self: Self,
        usecase: ActivateUserUseCase,
        repository: AsyncMock,
        user: User,
        activate_user: ActivateUserDto,
    ) -> None:
        repository.activate.return_value = True

        await usecase.execute(activate_user)

        usecase.repository.activate.assert_awaited_once_with(activate_user)  # type: ignore[attr-defined]  # noqa: E501

    async def test_activate_user_wrong_code(
        self: Self,
        usecase: ActivateUserUseCase,
        activate_user: ActivateUserDto,
        repository: AsyncMock,
    ) -> None:
        repository.activate.return_value = False

        with pytest.raises(WrongActivationCodeError):
            await usecase.execute(activate_user)

        usecase.repository.activate.assert_awaited_once_with(activate_user)  # type: ignore[attr-defined]  # noqa: E501


class TestGetUserByUsernameUseCase:
    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> GetUserByUsernameUseCase:
        return GetUserByUsernameUseCase(repository)

    async def test_get_user(
        self: Self,
        usecase: GetUserByUsernameUseCase,
        repository: AsyncMock,
        my_user: User,
    ) -> None:
        repository.get_by_username.return_value = my_user

        assert await usecase.execute(my_user.username) == my_user

        usecase.repository.get_by_username.assert_awaited_once_with(  # type: ignore[attr-defined]  # noqa: E501
            my_user.username,
        )

    async def test_user_not_found(
        self: Self,
        usecase: GetUserByUsernameUseCase,
        repository: AsyncMock,
    ) -> None:
        repository.get_by_username.return_value = None

        with pytest.raises(UserNotFoundError):
            await usecase.execute("test")

        usecase.repository.get_by_username.assert_awaited_once_with("test")  # type: ignore[attr-defined]  # noqa: E501


class TestGetUserByIdUseCase:
    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> GetUserByIdUseCase:
        return GetUserByIdUseCase(repository)

    async def test_get_user(
        self: Self,
        usecase: GetUserByIdUseCase,
        repository: AsyncMock,
        user: User,
    ) -> None:
        repository.get_by_id.return_value = user

        result = await usecase.execute(user.id)
        assert result == user

        usecase.repository.get_by_id.assert_awaited_once_with(user.id)  # type: ignore[attr-defined]  # noqa: E501

    async def test_user_not_found(
        self: Self,
        usecase: GetUserByIdUseCase,
        repository: AsyncMock,
    ) -> None:
        repository.get_by_id.return_value = None

        with pytest.raises(UserNotFoundError):
            await usecase.execute(1)

        usecase.repository.get_by_id.assert_awaited_once_with(1)  # type: ignore[attr-defined]  # noqa: E501


class TestResetPasswordUseCase:
    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> ResetPasswordUseCase:
        return ResetPasswordUseCase(repository)

    @pytest.fixture(autouse=True)
    def _mock(
        self: Self,
        repository: AsyncMock,
    ) -> None:
        repository.set_reset_password_code.return_value = True

    async def test_reset_password(
        self: Self,
        usecase: ResetPasswordUseCase,
        repository: AsyncMock,
        user: User,
    ) -> None:
        repository.set_reset_password_code.return_value = True
        repository.get_by_email.return_value = user

        result = await usecase.execute(user.email)
        assert result
        assert result.id == user.id

        usecase.repository.set_reset_password_code.assert_awaited_once()  # type: ignore[attr-defined]  # noqa: E501

    async def test_user_not_found(
        self: Self,
        usecase: ResetPasswordUseCase,
        repository: AsyncMock,
    ) -> None:
        repository.get_by_email.return_value = None

        with pytest.raises(UserNotFoundError):
            await usecase.execute("test")

        usecase.repository.set_reset_password_code.assert_not_awaited()  # type: ignore[attr-defined]  # noqa: E501


class TestChangePasswordUseCase:
    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> ChangePasswordUseCase:
        return ChangePasswordUseCase(repository)

    @pytest.fixture(autouse=True)
    def _mock(
        self: Self,
        repository: AsyncMock,
    ) -> None:
        repository.change_password.return_value = True

    @pytest.fixture()
    def data(
        self: Self,
        user: User,
    ) -> ChangePasswordDto:
        return ChangePasswordDto(
            id=user.id,
            old_password=SecretStr("old_password"),
            new_password=SecretStr("new_password"),
        )

    async def test_change_password(
        self: Self,
        usecase: ChangePasswordUseCase,
        repository: AsyncMock,
        data: ChangePasswordDto,
    ) -> None:
        repository.change_password.return_value = True

        await usecase.execute(data)

        usecase.repository.change_password.assert_awaited_once_with(data)  # type: ignore[attr-defined]  # noqa: E501

    async def test_wrong_password(
        self: Self,
        usecase: ChangePasswordUseCase,
        repository: AsyncMock,
        data: ChangePasswordDto,
    ) -> None:
        repository.change_password.return_value = False

        with pytest.raises(WrongPasswordError):
            await usecase.execute(data)

        usecase.repository.change_password.assert_awaited_once_with(data)  # type: ignore[attr-defined]  # noqa: E501


class TestChangePasswordByResetCodeUseCase:
    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> ChangePasswordByResetCodeUseCase:
        return ChangePasswordByResetCodeUseCase(repository)

    @pytest.fixture(autouse=True)
    def _mock(
        self: Self,
        repository: AsyncMock,
    ) -> None:
        repository.change_password_by_reset_code.return_value = True

    @pytest.fixture()
    def data(
        self: Self,
        user: User,
    ) -> ChangePasswordByResetCodeDto:
        return ChangePasswordByResetCodeDto(
            id=user.id,
            code=SecretStr("code"),
            new_password=SecretStr("new_password"),
        )

    async def test_change_password(
        self: Self,
        usecase: ChangePasswordByResetCodeUseCase,
        repository: AsyncMock,
        data: ChangePasswordByResetCodeDto,
        user: User,
    ) -> None:
        repository.get_by_id.return_value = user

        await usecase.execute(data)

        usecase.repository.get_by_id.assert_awaited_once_with(data.id)  # type: ignore[attr-defined]  # noqa: E501

        repository.change_password_by_reset_code.assert_awaited_once_with(  # type: ignore[attr-defined]  # noqa: E501
            data,
        )

    async def test_user_not_found(
        self: Self,
        usecase: ChangePasswordByResetCodeUseCase,
        repository: AsyncMock,
        data: ChangePasswordByResetCodeDto,
    ) -> None:
        repository.get_by_id.return_value = None

        with pytest.raises(UserNotFoundError):
            await usecase.execute(data)

        usecase.repository.get_by_id.assert_awaited_once_with(data.id)  # type: ignore[attr-defined]  # noqa: E501
        usecase.repository.change_password_by_reset_code.assert_not_awaited()  # type: ignore[attr-defined]  # noqa: E501

    async def test_wrong_code(
        self: Self,
        usecase: ChangePasswordByResetCodeUseCase,
        repository: AsyncMock,
        data: ChangePasswordByResetCodeDto,
        user: User,
    ) -> None:
        repository.get_by_id.return_value = user
        repository.change_password_by_reset_code.return_value = False

        with pytest.raises(WrongResetCodeError):
            await usecase.execute(data)

        usecase.repository.get_by_id.assert_awaited_once_with(data.id)  # type: ignore[attr-defined]  # noqa: E501
        repository.change_password_by_reset_code.assert_awaited_once_with(  # type: ignore[attr-defined]  # noqa: E501
            data,
        )
