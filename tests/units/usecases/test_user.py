from datetime import timezone
from unittest.mock import AsyncMock

import pytest
from faker import Faker
from pydantic import SecretStr
from pytest_mock import MockerFixture

from app.internal.entity.user import (
    ChangePasswordByResetCodeDto,
    ChangePasswordDto,
    NewUserDto,
    User,
)
from app.internal.usecase.exceptions.user import (
    UserAlreadyExistsException,
    UserNotFoundException,
    WrongActivationCodeException,
    WrongPasswordException,
    WrongResetCodeException,
)
from app.internal.usecase.repository.user import PostgresUserRepository
from app.internal.usecase.user import (
    ActivateUserUseCase,
    ChangePasswordByResetCodeUseCase,
    ChangePasswordUseCase,
    CreateUserUseCase,
    GetUserByIdUseCase,
    GetUserByUsernameUseCase,
    ResetPasswordUseCase,
)


@pytest.fixture
def repository(mocker: MockerFixture) -> PostgresUserRepository:
    session = mocker.MagicMock()
    return PostgresUserRepository(session)


@pytest.fixture
def user(faker: Faker) -> User:
    return User(
        id=faker.random_int(),
        username=faker.user_name(),
        email=faker.email(),
        created=faker.past_datetime(tzinfo=timezone.utc),
    )


@pytest.fixture
def my_user(faker: Faker) -> User:
    return User(
        id=faker.random_int(),
        username=faker.user_name(),
        is_admin=False,
        email=faker.email(),
        created=faker.past_datetime(tzinfo=timezone.utc),
    )


@pytest.fixture
def new_user(faker: Faker) -> NewUserDto:
    return NewUserDto(
        email=faker.email(),
        password=faker.password(),
        username=faker.user_name(),
    )


class TestCreateUserUseCase:
    @pytest.fixture(autouse=True)
    def mock(
        self,
        mocker: MockerFixture,
        faker: Faker,
        user: User,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.user."
            "PostgresUserRepository."
            "get_by_email",
            return_value=None,
        )
        mocker.patch(
            "app.internal.usecase.repository.user."
            "PostgresUserRepository."
            "get_by_username",
            return_value=None,
        )
        mocker.patch(
            "app.internal.usecase.repository.user."
            "PostgresUserRepository."
            "create",
            return_value=user,
        )

    @pytest.fixture
    def usecase(
        self,
        repository: PostgresUserRepository,
    ) -> CreateUserUseCase:
        return CreateUserUseCase(repository)

    async def test_create_user(
        self,
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
        self,
        usecase: AsyncMock,
        new_user: NewUserDto,
        user: User,
        mocker: MockerFixture,
        get_by: str,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.user.PostgresUserRepository."
            f"get_by_{get_by}",
            return_value=user,
        )

        with pytest.raises(UserAlreadyExistsException):
            await usecase.execute(new_user)

        usecase.repository.create.assert_not_awaited()


class TestActivateUserUseCase:
    @pytest.fixture
    def usecase(
        self,
        repository: PostgresUserRepository,
    ) -> ActivateUserUseCase:
        return ActivateUserUseCase(repository)

    async def test_activate_user(
        self,
        usecase: AsyncMock,
        mocker: MockerFixture,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.user.PostgresUserRepository."
            "activate",
            return_value=True,
        )

        assert await usecase.execute("test")

        usecase.repository.activate.assert_awaited_once_with("test")

    async def test_activate_user_wrong_code(
        self,
        usecase: AsyncMock,
        mocker: MockerFixture,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.user.PostgresUserRepository."
            "activate",
            return_value=False,
        )

        with pytest.raises(WrongActivationCodeException):
            await usecase.execute("test")

        usecase.repository.activate.assert_awaited_once_with("test")


class TestGetUserByUsernameUseCase:
    @pytest.fixture
    def usecase(
        self,
        repository: PostgresUserRepository,
    ) -> GetUserByUsernameUseCase:
        return GetUserByUsernameUseCase(repository)

    async def test_get_user(
        self,
        usecase: AsyncMock,
        mocker: MockerFixture,
        my_user: User,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.user.PostgresUserRepository."
            "get_by_username",
            return_value=my_user,
        )

        assert await usecase.execute(my_user.username) == my_user

        usecase.repository.get_by_username.assert_awaited_once_with(
            my_user.username,
        )

    async def test_user_not_found(
        self,
        usecase: AsyncMock,
        mocker: MockerFixture,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.user.PostgresUserRepository."
            "get_by_username",
            return_value=None,
        )

        with pytest.raises(UserNotFoundException):
            await usecase.execute("test")

        usecase.repository.get_by_username.assert_awaited_once_with("test")


class TestGetUserByIdUseCase:
    @pytest.fixture
    def usecase(
        self,
        repository: PostgresUserRepository,
    ) -> GetUserByIdUseCase:
        return GetUserByIdUseCase(repository)

    async def test_get_user(
        self,
        usecase: AsyncMock,
        mocker: MockerFixture,
        user: User,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.user.PostgresUserRepository."
            "get_by_id",
            return_value=user,
        )

        result = await usecase.execute(user.id)
        assert result == user

        usecase.repository.get_by_id.assert_awaited_once_with(user.id)

    async def test_user_not_found(
        self,
        usecase: AsyncMock,
        mocker: MockerFixture,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.user.PostgresUserRepository."
            "get_by_id",
            return_value=None,
        )

        with pytest.raises(UserNotFoundException):
            await usecase.execute(1)

        usecase.repository.get_by_id.assert_awaited_once_with(1)


class TestResetPasswordUseCase:
    @pytest.fixture
    def usecase(
        self,
        repository: PostgresUserRepository,
    ) -> ResetPasswordUseCase:
        return ResetPasswordUseCase(repository)

    @pytest.fixture(autouse=True)
    def mock(
        self,
        mocker: MockerFixture,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.user.PostgresUserRepository."
            "set_reset_password_code",
            return_value=True,
        )

    async def test_reset_password(
        self,
        usecase: AsyncMock,
        mocker: MockerFixture,
        user: User,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.user.PostgresUserRepository."
            "set_reset_password_code",
            return_value=True,
        )

        mocker.patch(
            "app.internal.usecase.repository.user.PostgresUserRepository."
            "get_by_email",
            return_value=user,
        )

        result = await usecase.execute(user.email)
        assert result
        assert result.id == user.id

        usecase.repository.set_reset_password_code.assert_awaited_once()

    async def test_user_not_found(
        self,
        usecase: AsyncMock,
        mocker: MockerFixture,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.user.PostgresUserRepository."
            "get_by_email",
            return_value=None,
        )

        with pytest.raises(UserNotFoundException):
            await usecase.execute("test")

        usecase.repository.set_reset_password_code.assert_not_awaited()


class TestChangePasswordUseCase:
    @pytest.fixture
    def usecase(
        self,
        repository: PostgresUserRepository,
    ) -> ChangePasswordUseCase:
        return ChangePasswordUseCase(repository)

    @pytest.fixture(autouse=True)
    def mock(
        self,
        mocker: MockerFixture,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.user.PostgresUserRepository."
            "change_password",
            return_value=True,
        )

    @pytest.fixture
    def data(
        self,
        user: User,
    ) -> ChangePasswordDto:
        return ChangePasswordDto(
            id=user.id,
            old_password=SecretStr("old_password"),
            new_password=SecretStr("new_password"),
        )

    async def test_change_password(
        self,
        usecase: AsyncMock,
        mocker: MockerFixture,
        data: ChangePasswordDto,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.user.PostgresUserRepository."
            "change_password",
            return_value=True,
        )

        assert await usecase.execute(data)

        usecase.repository.change_password.assert_awaited_once_with(data)

    async def test_wrong_password(
        self,
        usecase: AsyncMock,
        mocker: MockerFixture,
        data: ChangePasswordDto,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.user.PostgresUserRepository."
            "change_password",
            return_value=False,
        )

        with pytest.raises(WrongPasswordException):
            await usecase.execute(data)

        usecase.repository.change_password.assert_awaited_once_with(data)


class TestChangePasswordByResetCodeUseCase:
    @pytest.fixture
    def usecase(
        self,
        repository: PostgresUserRepository,
    ) -> ChangePasswordByResetCodeUseCase:
        return ChangePasswordByResetCodeUseCase(repository)

    @pytest.fixture(autouse=True)
    def mock(
        self,
        mocker: MockerFixture,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.user.PostgresUserRepository."
            "change_password_by_reset_code",
            return_value=True,
        )

    @pytest.fixture
    def data(
        self,
        user: User,
    ) -> ChangePasswordByResetCodeDto:
        return ChangePasswordByResetCodeDto(
            id=user.id,
            code=SecretStr("code"),
            new_password=SecretStr("new_password"),
        )

    async def test_change_password(
        self,
        usecase: AsyncMock,
        mocker: MockerFixture,
        data: ChangePasswordByResetCodeDto,
        user: User,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.user.PostgresUserRepository."
            "get_by_id",
            return_value=user,
        )

        assert await usecase.execute(data)

        usecase.repository.get_by_id.assert_awaited_once_with(data.id)

        usecase.repository.change_password_by_reset_code.assert_awaited_once_with(  # noqa: E501
            data
        )

    async def test_user_not_found(
        self,
        usecase: AsyncMock,
        mocker: MockerFixture,
        data: ChangePasswordByResetCodeDto,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.user.PostgresUserRepository."
            "get_by_id",
            return_value=None,
        )

        with pytest.raises(UserNotFoundException):
            await usecase.execute(data)

        usecase.repository.get_by_id.assert_awaited_once_with(data.id)
        usecase.repository.change_password_by_reset_code.assert_not_awaited()

    async def test_wrong_code(
        self,
        usecase: AsyncMock,
        mocker: MockerFixture,
        data: ChangePasswordByResetCodeDto,
        user: User,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.user.PostgresUserRepository."
            "get_by_id",
            return_value=user,
        )

        mocker.patch(
            "app.internal.usecase.repository.user.PostgresUserRepository."
            "change_password_by_reset_code",
            return_value=False,
        )

        with pytest.raises(WrongResetCodeException):
            await usecase.execute(data)

        usecase.repository.get_by_id.assert_awaited_once_with(data.id)
        usecase.repository.change_password_by_reset_code.assert_awaited_once_with(  # noqa: E501
            data
        )
