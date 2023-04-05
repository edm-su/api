from abc import ABC, abstractmethod
from datetime import datetime

from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Self

from app.db import users
from app.internal.entity.user import (
    ActivateUserDto,
    ChangePasswordByResetCodeDto,
    ChangePasswordDto,
    NewUserDto,
    ResetPasswordDto,
    User,
)


class AbstractUserRepository(ABC):
    @abstractmethod
    async def get_by_email(
        self: Self,
        email: str,
    ) -> User | None:
        pass

    @abstractmethod
    async def get_by_username(
        self: Self,
        username: str,
    ) -> User | None:
        pass

    @abstractmethod
    async def get_by_id(
        self: Self,
        user_id: int,
    ) -> User | None:
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
    ) -> bool:
        pass

    @abstractmethod
    async def set_reset_password_code(
        self: Self,
        data: ResetPasswordDto,
    ) -> bool:
        pass

    @abstractmethod
    async def change_password(
        self: Self,
        data: ChangePasswordDto,
    ) -> bool:
        pass

    @abstractmethod
    async def change_password_by_reset_code(
        self: Self,
        data: ChangePasswordByResetCodeDto,
    ) -> bool:
        pass


class PostgresUserRepository(AbstractUserRepository):
    def __init__(
        self: Self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def __get_by(
        self: Self,
        whereclauses: list,
    ) -> User | None:
        query = users.select()
        for whereclause in whereclauses:
            query = query.where(whereclause)

        result = await self.session.execute(query)
        result = result.first()
        return (
            User(
                id=result["id"],
                created=result["created"],
                password=SecretStr(result["password"]),
                email=result["email"],
                username=result["username"],
                is_active=result["is_active"],
                is_admin=result["is_admin"],
                is_banned=result["is_banned"],
                last_login=result["last_login"],
                last_login_ip=result["last_login_ip"],
                activation_code=SecretStr(result["activation_code"]),
            )
            if result
            else None
        )

    async def get_by_email(
        self: Self,
        email: str,
    ) -> User | None:
        return await self.__get_by([users.c.email == email])

    async def get_by_username(
        self: Self,
        username: str,
    ) -> User | None:
        return await self.__get_by([users.c.username == username])

    async def get_by_id(
        self: Self,
        user_id: int,
    ) -> User | None:
        return await self.__get_by([users.c.id == user_id])

    async def create(
        self: Self,
        new_user: NewUserDto,
    ) -> User:
        if new_user.hashed_password is None:
            error_text = "hashed_password is None"
            raise ValueError(error_text)
        if new_user.activation_code is None:
            error_text = "activation_code is None"
            raise ValueError(error_text)

        values = {
            "username": new_user.username,
            "email": new_user.email,
            "password": new_user.hashed_password.get_secret_value(),
            "activation_code": new_user.activation_code.get_secret_value(),
        }
        query = users.insert().values(values).returning(users)
        result = await self.session.execute(query)
        result = result.first()
        return User(
            id=result["id"],
            created=result["created"],
            password=SecretStr(result["password"]),
            email=result["email"],
            username=result["username"],
            is_active=result["is_activate"],
            is_admin=result["is_admin"],
            is_banned=result["is_banned"],
            last_login=result["last_login"],
            last_login_ip=result["last_login_ip"],
            activation_code=SecretStr(result["activation_code"]),
        )

    async def activate(
        self: Self,
        code: ActivateUserDto,
    ) -> bool:
        query = users.update()
        query = query.where(users.c.is_activate.is_(False))  # noqa: FBT003
        query = query.where(
            users.c.activation_code == code.activation_code.get_secret_value(),
        )
        query = query.where(users.c.id == code.id)
        query = query.values(is_activate=True, activation_code=None)
        return bool(await self.session.execute(query))

    async def set_reset_password_code(
        self: Self,
        data: ResetPasswordDto,
    ) -> bool:
        query = users.update().where(users.c.id == data.id)
        query = query.values(
            {
                "recovery_code": data.code.get_secret_value(),
                "recovery_code_lifetime_end": data.expires,
            },
        )
        return bool(await self.session.execute(query))

    async def change_password(
        self: Self,
        data: ChangePasswordDto,
    ) -> bool:
        query = users.update().where(users.c.id == data.id)
        query = query.where(users.c.password == data.hashed_old_password)

        if data.hashed_new_password is None:
            error_text = "hashed_new_password is None"
            raise ValueError(error_text)
        query = query.values(
            {
                "password": data.hashed_new_password.get_secret_value(),
                "recovery_code": None,
                "recovery_code_lifetime_end": None,
            },
        )
        return bool(await self.session.execute(query))

    async def change_password_by_reset_code(
        self: Self,
        data: ChangePasswordByResetCodeDto,
    ) -> bool:
        query = users.update().where(users.c.id == data.id)
        query = query.where(users.c.recovery_code == data.code)
        query = query.where(
            users.c.recovery_code_lifetime_end > datetime.now(),
        )
        if data.hashed_new_password is None:
            error_text = "hashed_new_password is None"
            raise ValueError(error_text)
        query = query.values(
            {
                "password": data.hashed_new_password.get_secret_value(),
                "recovery_code": None,
                "recovery_code_lifetime_end": None,
            },
        )
        return bool(await self.session.execute(query))
