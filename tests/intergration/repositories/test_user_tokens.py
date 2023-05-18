import pytest
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Self

from app.internal.entity.user import User, UserToken, UserTokenDTO
from app.internal.usecase.repository.user_tokens import (
    PostgresUserTokensRepository,
)


class TestPostgresUserTokensRepository:
    @pytest.fixture()
    def repository(
        self: Self,
        pg_session: AsyncSession,
    ) -> PostgresUserTokensRepository:
        return PostgresUserTokensRepository(
            session=pg_session,
        )

    @pytest.fixture()
    def user_token_data(
        self: Self,
        faker: Faker,
    ) -> UserTokenDTO:
        return UserTokenDTO(
            name=faker.name(),
            expired_at=faker.date_time(),
        )

    @pytest.fixture()
    async def user_token(
        self: Self,
        repository: PostgresUserTokensRepository,
        pg_user: User,
        user_token_data: UserTokenDTO,
    ) -> UserToken:
        return await repository.create(
            token=user_token_data,
            user=pg_user,
        )

    async def test_create(
        self: Self,
        repository: PostgresUserTokensRepository,
        user_token_data: UserTokenDTO,
        pg_user: User,
    ) -> None:
        user_token = await repository.create(
            token=user_token_data,
            user=pg_user,
        )

        assert isinstance(user_token, UserToken)
        assert user_token.name == user_token_data.name

    async def test_get_user_tokens(
        self: Self,
        repository: PostgresUserTokensRepository,
        pg_user: User,
        user_token: UserToken,
    ) -> None:
        user_tokens = await repository.get_user_tokens(
            user=pg_user,
        )

        assert isinstance(user_tokens, list)
        assert len(user_tokens) > 0
        assert user_token.id in [
            user_token.id
            for user_token in user_tokens
            if user_token is not None
        ]

        pg_user.id = 999_999
        user_tokens = await repository.get_user_tokens(
            user=pg_user,
        )

        assert len(user_tokens) == 0

    async def test_get_by_id(
        self: Self,
        repository: PostgresUserTokensRepository,
        pg_user: User,
        user_token: UserToken,
    ) -> None:
        token = await repository.get_by_id(
            id_=user_token.id,
            user=pg_user,
        )

        assert isinstance(token, UserToken)
        assert token.id == user_token.id

        token = await repository.get_by_id(
            id_=999_999,
            user=pg_user,
        )

        assert token is None

        pg_user.id = 999_999
        token = await repository.get_by_id(
            id_=user_token.id,
            user=pg_user,
        )

        assert token is None

    async def test_revoke(
        self: Self,
        repository: PostgresUserTokensRepository,
        pg_user: User,
        user_token: UserToken,
    ) -> None:
        await repository.revoke(
            token=user_token,
            user=pg_user,
        )

        token = await repository.get_by_id(
            id_=user_token.id,
            user=pg_user,
        )

        assert token is None
