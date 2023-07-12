from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from faker import Faker
from pydantic import SecretStr
from pytest_mock import MockFixture
from typing_extensions import Self

from app.internal.entity.user import (
    User,
    UserToken,
    UserTokenDTO,
    get_password_hash,
)
from app.internal.usecase.exceptions.user_tokens import UserTokenNotFoundError
from app.internal.usecase.repository.user_tokens import (
    AbstractUserTokensRepository,
)
from app.internal.usecase.user_tokens import (
    CreateUserTokenUseCase,
    GetAllUserTokensUseCase,
    RevokeUserTokenUseCase,
)


@pytest.fixture()
def repository(mocker: MockFixture) -> AsyncMock:
    return mocker.AsyncMock(spec=AbstractUserTokensRepository)


@pytest.fixture()
def user_token(faker: Faker) -> UserToken:
    return UserToken(
        id=faker.pyint(min_value=1),
        name=faker.sentence(),
        created_at=datetime.now(),
        expired_at=faker.date_time_between(
            start_date="now",
            end_date="+1y",
        ),
    )


@pytest.fixture()
def user(faker: Faker) -> User:
    return User(
        id=faker.pyint(min_value=1),
        username=faker.pystr(),
        email=faker.email(),
        created=faker.date_time_between(
            start_date="-30d",
            end_date="now",
        ),
        password=SecretStr(get_password_hash(faker.password())),
    )


class TestGetAllUserTokensUseCase:
    @pytest.fixture(autouse=True)
    def _mock(
        self: Self,
        repository: AsyncMock,
        user_token: UserToken,
    ) -> None:
        repository.get_user_tokens.return_value = [user_token]

    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> GetAllUserTokensUseCase:
        return GetAllUserTokensUseCase(repository)

    async def test_get_user_tokens(
        self: Self,
        usecase: GetAllUserTokensUseCase,
        repository: AsyncMock,
        user_token: UserToken,
        user: User,
    ) -> None:
        result = await usecase.execute(user)

        assert result == [user_token]

        repository.get_user_tokens.assert_awaited_once_with(user)


class TestCreateUserTokenUseCase:
    @pytest.fixture(autouse=True)
    def _mock(
        self: Self,
        repository: AsyncMock,
        user_token: UserToken,
    ) -> None:
        repository.create.return_value = user_token

    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> CreateUserTokenUseCase:
        return CreateUserTokenUseCase(repository)

    async def test_create_user_token(
        self: Self,
        usecase: CreateUserTokenUseCase,
        repository: AsyncMock,
        user_token: UserToken,
        user: User,
    ) -> None:
        token = UserTokenDTO(
            name=user_token.name,
            expired_at=user_token.expired_at,
        )
        result = await usecase.execute(token, user)

        assert result == user_token

        repository.create.assert_awaited_once_with(token, user)


class TestRevokeUserTokenUseCase:
    @pytest.fixture(autouse=True)
    def _mock(
        self: Self,
        repository: AsyncMock,
        user_token: UserToken,
    ) -> None:
        repository.revoke.return_value = None
        repository.get_by_id.return_value = user_token

    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> RevokeUserTokenUseCase:
        return RevokeUserTokenUseCase(repository)

    async def test_revoke_user_token(
        self: Self,
        usecase: RevokeUserTokenUseCase,
        repository: AsyncMock,
        user_token: UserToken,
        user: User,
    ) -> None:
        await usecase.execute(user_token.id, user)

        repository.revoke.assert_awaited_once_with(user_token, user)
        repository.get_by_id.assert_awaited_once_with(user_token.id, user)

    async def test_revoke_user_token_not_found(
        self: Self,
        usecase: RevokeUserTokenUseCase,
        repository: AsyncMock,
        user: User,
        user_token: UserToken,
    ) -> None:
        repository.get_by_id.return_value = None
        with pytest.raises(UserTokenNotFoundError):
            await usecase.execute(user_token.id, user)
