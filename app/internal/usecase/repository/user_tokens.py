from abc import ABC, abstractmethod
from datetime import datetime

from sqlalchemy import insert, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Self

from app.internal.entity.user import User, UserToken, UserTokenDTO
from app.internal.usecase.exceptions.user_tokens import UserTokenNotFoundError
from app.pkg.postgres import UserToken as PGUserToken


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
    ) -> list[UserToken]:
        pass

    @abstractmethod
    async def get_by_id(
        self: Self,
        id_: int,
        user: User,
    ) -> UserToken:
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
        query = (
            insert(PGUserToken)
            .values(
                name=token.name,
                user_id=user.id,
                expired_at=token.expired_at,
            )
            .returning(PGUserToken)
        )

        result = (await self._session.scalars(query)).one()
        return UserToken.from_orm(result)

    async def get_user_tokens(
        self: Self,
        user: User,
    ) -> list[UserToken]:
        query = select(PGUserToken).where(
            (PGUserToken.user_id == user.id)
            & (PGUserToken.revoked_at.is_(None)),
        )

        result = (await self._session.scalars(query)).all()
        return [UserToken.from_orm(token) for token in result]

    async def get_by_id(
        self: Self,
        id_: int,
        user: User,
    ) -> UserToken:
        query = select(PGUserToken).where(
            (PGUserToken.id == id_)
            & (PGUserToken.user_id == user.id)
            & (PGUserToken.revoked_at.is_(None)),
        )

        try:
            result = (await self._session.scalars(query)).one()
            return UserToken.from_orm(result)
        except NoResultFound as e:
            raise UserTokenNotFoundError from e

    async def revoke(
        self: Self,
        token: UserToken,
        user: User,
    ) -> None:
        query = (
            update(PGUserToken)
            .where(
                (PGUserToken.id == token.id)
                & (PGUserToken.user_id == user.id)
                & (PGUserToken.revoked_at.is_(None)),
            )
            .values(revoked_at=datetime.utcnow())
            .returning(PGUserToken.revoked_at)
        )

        try:
            (await self._session.scalars(query)).one()
        except NoResultFound as e:
            raise UserTokenNotFoundError from e
