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
    SignInDto,
    User,
    get_password_hash,
)
from app.internal.usecase.exceptions.user import (
    UserAlreadyExistsError,
    UserError,
    UserIsBannedError,
    UserIsNotActivatedError,
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
    SignInUseCase,
    verify_password,
)
from app.pkg.nats import NatsClient


@pytest.fixture()
def repository(mocker: MockerFixture) -> AbstractUserRepository:
    return AsyncMock(repr=AbstractUserRepository)


@pytest.fixture()
def broker(mocker: MockerFixture) -> AsyncMock:
    return AsyncMock(repr=NatsClient)


@pytest.fixture()
def user(faker: Faker) -> User:
    return User(
        id=faker.random_int(),
        username=faker.user_name(),
        email=faker.email(),
        created=faker.past_datetime(tzinfo=timezone.utc),
        password=faker.password(),
    )


@pytest.fixture()
def my_user(faker: Faker) -> User:
    return User(
        id=faker.random_int(),
        username=faker.user_name(),
        is_admin=False,
        email=faker.email(),
        created=faker.past_datetime(tzinfo=timezone.utc),
        password=SecretStr(get_password_hash(faker.password())),
    )


@pytest.fixture()
def new_user(faker: Faker) -> NewUserDto:
    return NewUserDto(
        email=faker.email(),
        password=faker.password(),
        username=faker.user_name(),
    )


class TestCreateUserUseCase:
    @pytest.fixture()
    def _mock(
        self: Self,
        user: User,
        repository: AsyncMock,
    ) -> None:
        repository.get_by_email.side_effect = UserNotFoundError
        repository.get_by_username.side_effect = UserNotFoundError
        repository.create.return_value = user

    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
        broker: AsyncMock,
    ) -> CreateUserUseCase:
        return CreateUserUseCase(repository, broker)

    @pytest.mark.usefixtures("_mock")
    async def test_create_user(
        self: Self,
        usecase: AsyncMock,
        new_user: NewUserDto,
        user: User,
        repository: AsyncMock,
        broker: AsyncMock,
    ) -> None:
        assert await usecase.execute(new_user) == user

        repository.get_by_email.assert_awaited_once_with(new_user.email)
        repository.get_by_username.assert_awaited_once_with(new_user.username)
        repository.create.assert_awaited_once()
        broker.publish.assert_awaited_once()

    @pytest.mark.parametrize("get_by", ["email", "username"])
    async def test_create_already_exists_user(
        self: Self,
        usecase: AsyncMock,
        new_user: NewUserDto,
        user: User,
        repository: AsyncMock,
        get_by: str,
        broker: AsyncMock,
    ) -> None:
        if get_by == "email":
            repository_method = repository.get_by_email
        else:
            repository_method = repository.get_by_username
        repository_method.return_value = user

        with pytest.raises(UserAlreadyExistsError):
            await usecase.execute(new_user)

        repository.create.assert_not_awaited()
        broker.publish.assert_not_awaited()


class TestActivateUserUseCase:
    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
        broker: AsyncMock,
    ) -> ActivateUserUseCase:
        return ActivateUserUseCase(repository, broker)

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
        usecase: AsyncMock,
        repository: AsyncMock,
        activate_user: ActivateUserDto,
    ) -> None:
        repository.activate.return_value = True

        await usecase.execute(activate_user)

        repository.activate.assert_awaited_once_with(activate_user)

    async def test_activate_user_wrong_code(
        self: Self,
        usecase: AsyncMock,
        activate_user: ActivateUserDto,
        repository: AsyncMock,
    ) -> None:
        repository.activate.side_effect = UserNotFoundError

        with pytest.raises(WrongActivationCodeError):
            await usecase.execute(activate_user)

        repository.activate.assert_awaited_once_with(activate_user)


class TestGetUserByUsernameUseCase:
    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
        broker: AsyncMock,
    ) -> GetUserByUsernameUseCase:
        return GetUserByUsernameUseCase(repository, broker)

    async def test_get_user(
        self: Self,
        usecase: AsyncMock,
        repository: AsyncMock,
        my_user: User,
    ) -> None:
        repository.get_by_username.return_value = my_user

        assert await usecase.execute(my_user.username) == my_user

        repository.get_by_username.assert_awaited_once_with(my_user.username)

    async def test_user_not_found(
        self: Self,
        usecase: AsyncMock,
        repository: AsyncMock,
    ) -> None:
        repository.get_by_username.return_value = None

        with pytest.raises(UserNotFoundError):
            await usecase.execute("test")

        repository.get_by_username.assert_awaited_once_with("test")


class TestGetUserByIdUseCase:
    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
        broker: AsyncMock,
    ) -> GetUserByIdUseCase:
        return GetUserByIdUseCase(repository, broker)

    async def test_get_user(
        self: Self,
        usecase: AsyncMock,
        repository: AsyncMock,
        user: User,
    ) -> None:
        repository.get_by_id.return_value = user

        result = await usecase.execute(user.id)
        assert result == user

        repository.get_by_id.assert_awaited_once_with(user.id)

    async def test_user_not_found(
        self: Self,
        usecase: GetUserByIdUseCase,
        repository: AsyncMock,
    ) -> None:
        repository.get_by_id.return_value = None

        with pytest.raises(UserNotFoundError):
            await usecase.execute(1)

        repository.get_by_id.assert_awaited_once_with(1)


class TestResetPasswordUseCase:
    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
        broker: AsyncMock,
    ) -> ResetPasswordUseCase:
        return ResetPasswordUseCase(repository, broker)

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
        broker: AsyncMock,
    ) -> None:
        repository.set_reset_password_code.return_value = True
        repository.get_by_email.return_value = user

        await usecase.execute(user.email)

        repository.set_reset_password_code.assert_awaited_once()
        broker.publish.assert_awaited_once()

    async def test_user_not_found(
        self: Self,
        usecase: ResetPasswordUseCase,
        repository: AsyncMock,
        broker: AsyncMock,
    ) -> None:
        repository.get_by_email.side_effect = UserNotFoundError

        with pytest.raises(UserNotFoundError):
            await usecase.execute("test")

        repository.set_reset_password_code.assert_not_awaited()
        broker.publish.assert_not_awaited()

    async def test_set_code_error(
        self: Self,
        usecase: ResetPasswordUseCase,
        repository: AsyncMock,
    ) -> None:
        repository.set_reset_password_code.side_effect = UserNotFoundError

        with pytest.raises(UserError):
            await usecase.execute("test")


class TestChangePasswordUseCase:
    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
        broker: AsyncMock,
    ) -> ChangePasswordUseCase:
        return ChangePasswordUseCase(repository, broker)

    @pytest.fixture()
    def data(
        self: Self,
        user: User,
    ) -> ChangePasswordDto:
        return ChangePasswordDto(
            user_id=user.id,
            old_password=SecretStr("old_password"),
            new_password=SecretStr("new_password"),
        )

    async def test_change_password(
        self: Self,
        usecase: ChangePasswordUseCase,
        repository: AsyncMock,
        data: ChangePasswordDto,
        user: User,
        mocker: MockerFixture,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.user.verify_password",
            return_value=None,
        )
        repository.get_by_id.return_value = user
        repository.change_password.return_value = None

        await usecase.execute(data)

        repository.get_by_id.assert_awaited_once_with(user.id)
        repository.change_password.assert_awaited_once_with(data)

    async def test_wrong_password(
        self: Self,
        usecase: ChangePasswordUseCase,
        repository: AsyncMock,
        data: ChangePasswordDto,
        mocker: MockerFixture,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.user.verify_password",
            side_effect=WrongPasswordError,
        )
        with pytest.raises(WrongPasswordError):
            await usecase.execute(data)

        repository.change_password.assert_not_awaited()

    async def test_change_error(
        self: Self,
        usecase: ChangePasswordUseCase,
        repository: AsyncMock,
        data: ChangePasswordDto,
        mocker: MockerFixture,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.user.verify_password",
            return_value=None,
        )
        repository.change_password.side_effect = UserNotFoundError

        with pytest.raises(WrongPasswordError):
            await usecase.execute(data)

        repository.change_password.assert_awaited_once_with(data)
        repository.get_by_id.assert_awaited_once_with(data.user_id)


class TestChangePasswordByResetCodeUseCase:
    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
        broker: AsyncMock,
    ) -> ChangePasswordByResetCodeUseCase:
        return ChangePasswordByResetCodeUseCase(repository, broker)

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
            user_id=user.id,
            code=SecretStr("AAAAAAAAAA"),
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

        repository.change_password_by_reset_code.assert_awaited_once_with(
            data,
        )

    async def test_user_not_found(
        self: Self,
        usecase: ChangePasswordByResetCodeUseCase,
        repository: AsyncMock,
        data: ChangePasswordByResetCodeDto,
    ) -> None:
        repository.change_password_by_reset_code.side_effect = (
            UserNotFoundError
        )

        with pytest.raises(WrongResetCodeError):
            await usecase.execute(data)

        repository.change_password_by_reset_code.assert_awaited_once_with(data)

    async def test_wrong_code(
        self: Self,
        usecase: ChangePasswordByResetCodeUseCase,
        repository: AsyncMock,
        data: ChangePasswordByResetCodeDto,
    ) -> None:
        repository.change_password_by_reset_code.side_effect = (
            UserNotFoundError
        )

        with pytest.raises(WrongResetCodeError):
            await usecase.execute(data)

        repository.change_password_by_reset_code.assert_awaited_once_with(
            data,
        )


class TestSignInUseCase:
    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
        broker: AsyncMock,
    ) -> SignInUseCase:
        return SignInUseCase(repository, broker)

    @pytest.fixture()
    def _mock(
        self: Self,
        repository: AsyncMock,
        user: User,
    ) -> None:
        user.is_active = True
        repository.get_by_email.return_value = user

    @pytest.fixture()
    def _mock_verify_password(self: Self, mocker: MockerFixture) -> None:
        mocker.patch(
            "app.internal.usecase.user.verify_password",
            return_value=None,
        )

    @pytest.fixture()
    def data(
        self: Self,
        user: User,
    ) -> SignInDto:
        return SignInDto(
            email=user.email,
            password=SecretStr("password"),
        )

    @pytest.mark.usefixtures("_mock", "_mock_verify_password")
    async def test_sign_in(
        self: Self,
        usecase: SignInUseCase,
        repository: AsyncMock,
        data: SignInDto,
    ) -> None:
        result = await usecase.execute(data)

        repository.get_by_email.assert_awaited_once_with(data.email)
        assert result

    @pytest.mark.usefixtures("_mock")
    async def test_wrong_password(
        self: Self,
        usecase: SignInUseCase,
        repository: AsyncMock,
        data: SignInDto,
        mocker: MockerFixture,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.user.verify_password",
            side_effect=WrongPasswordError,
        )

        with pytest.raises(WrongPasswordError):
            await usecase.execute(data)
        repository.get_by_email.assert_awaited_once_with(data.email)

    async def test_user_is_banned(
        self: Self,
        usecase: SignInUseCase,
        repository: AsyncMock,
        data: SignInDto,
        user: User,
    ) -> None:
        user.is_banned = True
        repository.get_by_email.return_value = user

        with pytest.raises(UserIsBannedError):
            await usecase.execute(data)
        repository.get_by_email.assert_awaited_once_with(data.email)

    async def test_user_is_not_active(
        self: Self,
        usecase: SignInUseCase,
        repository: AsyncMock,
        data: SignInDto,
        user: User,
    ) -> None:
        user.is_active = False
        repository.get_by_email.return_value = user

        with pytest.raises(UserIsNotActivatedError):
            await usecase.execute(data)
        repository.get_by_email.assert_awaited_once_with(data.email)


class TestVeryfyPassword:
    def test_verify_password(self: Self) -> None:
        password = "password"
        hashed_password = get_password_hash(password)
        verify_password("password", hashed_password)

    def test_wrong_password(self: Self) -> None:
        password = "password"
        hashed_password = get_password_hash(password)
        with pytest.raises(WrongPasswordError):
            verify_password("wrong_password", hashed_password)
