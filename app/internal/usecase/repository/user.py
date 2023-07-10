from abc import ABC, abstractmethod
from datetime import datetime

from sqlalchemy import ColumnExpressionArgument, false, insert, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Self

from app.internal.entity.user import (
    ActivateUserDto,
    ChangePasswordByResetCodeDto,
    ChangePasswordDto,
    NewUserDto,
    ResetPasswordDto,
    User,
)
from app.internal.usecase.exceptions.user import (
    HashedPasswordRequiredError,
    UserNotFoundError,
)
from app.pkg.postgres import User as PGUser


class AbstractUserRepository(ABC):
    @abstractmethod
    async def get_by_email(
        self: Self,
        email: str,
    ) -> User:
        pass

    @abstractmethod
    async def get_by_username(
        self: Self,
        username: str,
    ) -> User:
        pass

    @abstractmethod
    async def get_by_id(
        self: Self,
        user_id: int,
    ) -> User:
        pass

    @abstractmethod
    async def create(
        self: Self,
        user: NewUserDto,
    ) -> User:
        pass

    @abstractmethod
    async def activate(
        self: Self,
        code: ActivateUserDto,
    ) -> None:
        pass

    @abstractmethod
    async def set_reset_password_code(
        self: Self,
        data: ResetPasswordDto,
    ) -> None:
        pass

    @abstractmethod
    async def change_password(
        self: Self,
        data: ChangePasswordDto,
    ) -> None:
        pass

    @abstractmethod
    async def change_password_by_reset_code(
        self: Self,
        data: ChangePasswordByResetCodeDto,
    ) -> None:
        pass


class PostgresUserRepository(AbstractUserRepository):
    def __init__(
        self: Self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def __get_by(
        self: Self,
        whereclauses: list[ColumnExpressionArgument[bool]],
    ) -> User:
        query = select(PGUser)
        for whereclause in whereclauses:
            query = query.where(whereclause)

        try:
            result = (await self._session.scalars(query)).one()
            return User.model_validate(result)
        except NoResultFound as e:
            raise UserNotFoundError from e

    async def get_by_email(
        self: Self,
        email: str,
    ) -> User:
        return await self.__get_by([PGUser.email == email])

    async def get_by_username(
        self: Self,
        username: str,
    ) -> User:
        return await self.__get_by([PGUser.username == username])

    async def get_by_id(
        self: Self,
        user_id: int,
    ) -> User:
        return await self.__get_by([PGUser.id == user_id])

    async def create(
        self: Self,
        new_user: NewUserDto,
    ) -> User:
        if not new_user.hashed_password:
            raise HashedPasswordRequiredError

        query = (
            insert(PGUser)
            .values(
                username=new_user.username,
                email=new_user.email,
                is_active=new_user.is_active,
                activation_code=(
                    new_user.activation_code.get_secret_value()
                    if new_user.activation_code
                    else None
                ),
                password=(
                    new_user.hashed_password.get_secret_value()
                    if new_user.hashed_password
                    else None
                ),
            )
            .returning(PGUser)
        )

        result = (await self._session.scalars(query)).one()
        return User.model_validate(result)

    async def activate(
        self: Self,
        code: ActivateUserDto,
    ) -> None:
        query = (
            update(PGUser)
            .where(PGUser.id == code.id)
            .where(PGUser.is_active == false())
            .where(PGUser.activation_code == code.activation_code)
            .values(is_active=True, activation_code=None)
            .returning(PGUser)
        )

        try:
            (await self._session.scalars(query)).one()
        except NoResultFound as e:
            raise UserNotFoundError from e

    async def set_reset_password_code(
        self: Self,
        data: ResetPasswordDto,
    ) -> None:
        query = (
            update(PGUser)
            .where(PGUser.id == data.id)
            .values(
                recovery_code=data.code.get_secret_value(),
                recovery_code_lifetime_end=data.expires,
            )
            .returning(PGUser)
        )

        try:
            (await self._session.scalars(query)).one()
        except NoResultFound as e:
            raise UserNotFoundError from e

    async def change_password(
        self: Self,
        data: ChangePasswordDto,
    ) -> None:
        if data.hashed_new_password is None:
            error_text = "hashed_new_password is None"
            raise ValueError(error_text)

        query = (
            update(PGUser)
            .where(PGUser.id == data.id)
            .values(
                password=data.hashed_new_password.get_secret_value(),
                recovery_code=None,
                recovery_code_lifetime_end=None,
            )
            .returning(PGUser)
        )

        try:
            (await self._session.scalars(query)).one()
        except NoResultFound as e:
            raise UserNotFoundError from e

    async def change_password_by_reset_code(
        self: Self,
        data: ChangePasswordByResetCodeDto,
    ) -> None:
        if not data.hashed_new_password:
            raise HashedPasswordRequiredError

        query = (
            update(PGUser)
            .where(
                (PGUser.id == data.id)
                & (PGUser.recovery_code == data.code.get_secret_value())
                & (PGUser.recovery_code_lifetime_end > datetime.now()),
            )
            .values(
                password=data.hashed_new_password.get_secret_value(),
                recovery_code=None,
                recovery_code_lifetime_end=None,
            )
            .returning(PGUser)
        )

        try:
            (await self._session.scalars(query)).one()
        except NoResultFound as e:
            raise UserNotFoundError from e
