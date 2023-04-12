from abc import ABC, abstractmethod
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Self

from app.db import users_tokens
from app.internal.entity.user import User, UserToken, UserTokenDTO


class AbstractUserTokensRepository(ABC):
    @abstractmethod
    async def create(
        self: Self,
        token: UserTokenDTO,
        user: User,
    ) -> UserToken:
        pass

    @abstractmethod
    async def get_user_tokens(
        self: Self,
        user: User,
    ) -> list[UserToken | None]:
        pass

    @abstractmethod
    async def get_by_id(
        self: Self,
        id_: int,
        user: User,
    ) -> UserToken | None:
        pass

    @abstractmethod
    async def revoke(
        self: Self,
        token: UserToken,
        user: User,
    ) -> None:
        pass

class PostgresUserTokensRepository(AbstractUserTokensRepository):
    def __init__(
        self: Self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def create(
        self: Self,
        token: UserTokenDTO,
        user: User,
    ) -> UserToken:
        values = {
            "name": token.name,
            "user_id": user.id,
            "expired_at": token.expired_at,
        }

        query = users_tokens.insert(values)
        query = query.returning(users_tokens.c.id, users_tokens.c.created_at)

        result = await self._session.execute(query)
        result = result.first()
        return UserToken(
            id=result["id"],
            name=token.name,
            expired_at=token.expired_at,
            created_at=result["created_at"],
        )

    async def get_user_tokens(
        self: Self,
        user: User,
    ) -> list[UserToken | None]:
        query = users_tokens.select().where(
            (users_tokens.c.user_id == user.id) &
            (users_tokens.c.revoked_at.is_(None)),
        )
        result = await self._session.execute(query)
        result = result.scalars().all()
        return [
            UserToken(
                id=token["id"],
                name=token["name"],
                expired_at=token["expired_at"],
                created_at=token["created_at"],
            )
            for token in result
        ]

    async def get_by_id(
        self: Self,
        id_: int,
        user: User,
    ) -> UserToken | None:
        query = users_tokens.select().where(
            (users_tokens.c.id == id_) &
            (users_tokens.c.user_id == user.id) &
            (users_tokens.c.revoked_at.is_(None)),
        )
        result = await self._session.execute(query)
        result = result.scalars().first()
        return UserToken(
            id=result["id"],
            name=result["name"],
            expired_at=result["expired_at"],
            created_at=result["created_at"],
        )

    async def revoke(
        self: Self,
        token: UserToken,
        user: User,
    ) -> None:
        values = {
            "revoked_at": datetime.utcnow(),
        }
        query = users_tokens.update(values).where(
            (users_tokens.c.id == token.id) &
            (users_tokens.c.user_id == user.id),
        )
        return await self._session.execute(query)
