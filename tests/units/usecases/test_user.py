from unittest.mock import AsyncMock

import pytest
from faker import Faker
from pytest_mock import MockerFixture

from app.internal.entity.user import CreateUser, MyUser, User
from app.internal.usecase.exceptions.user import (
    UserAlreadyExistsException,
    UserNotFoundException,
    WrongActivationCodeException,
)
from app.internal.usecase.repository.user import PostgresUserRepository
from app.internal.usecase.user import (
    ActivateUserUseCase,
    CreateUserUseCase,
    GetUserByIdUseCase,
    GetUserByUsernameUseCase,
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
        is_admin=False,
    )


@pytest.fixture
def my_user(faker: Faker) -> MyUser:
    return MyUser(
        id=faker.random_int(),
        username=faker.user_name(),
        is_admin=False,
        email=faker.email(),
    )


@pytest.fixture
def new_user(faker: Faker) -> CreateUser:
    return CreateUser(
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
        new_user: CreateUser,
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
        new_user: CreateUser,
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
        my_user: MyUser,
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
        my_user: MyUser,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.user.PostgresUserRepository."
            "get_by_id",
            return_value=user,
        )

        result = await usecase.execute(user.id)
        assert result == user
        assert result != my_user

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
