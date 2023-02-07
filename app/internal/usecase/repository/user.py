from abc import ABC, abstractmethod
from datetime import datetime

from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession

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
    async def get_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    async def create(self, user: NewUserDto) -> User:
        pass

    @abstractmethod
    async def activate(self, code: ActivateUserDto) -> bool:
        pass

    @abstractmethod
    async def set_reset_password_code(self, data: ResetPasswordDto) -> bool:
        pass

    @abstractmethod
    async def change_password(self, data: ChangePasswordDto) -> bool:
        pass

    @abstractmethod
    async def change_password_by_reset_code(
        self,
        data: ChangePasswordByResetCodeDto,
    ) -> bool:
        pass


class PostgresUserRepository(AbstractUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def __get_by(self, whereclauses: list) -> User | None:
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

    async def get_by_email(self, email: str) -> User | None:
        return await self.__get_by([users.c.email == email])

    async def get_by_username(self, username: str) -> User | None:
        return await self.__get_by([users.c.username == username])

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.__get_by([users.c.id == user_id])

    async def create(self, new_user: NewUserDto) -> User:
        if new_user.hashed_password is None:
            raise ValueError("hashed_password is None")
        if new_user.activation_code is None:
            raise ValueError("activation_code is None")

        values = {
            "username": new_user.username,
            "email": new_user.email,
            "password": new_user.hashed_password.get_secret_value(),
            "activation_code": new_user.activation_code.get_secret_value(),
        }
        query = users.insert().values(values).returning(users)
        result = await self.session.execute(query)
        result = result.first()
        user = User(
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
        return user

    async def activate(self, code: ActivateUserDto) -> bool:
        query = users.update().where(users.c.is_activate.is_(False))
        query = query.where(
            users.c.activation_code == code.activation_code.get_secret_value()
        )
        query = query.where(users.c.id == code.id)
        query = query.values(is_activate=True, activation_code=None)
        return bool(await self.session.execute(query))

    async def set_reset_password_code(self, data: ResetPasswordDto) -> bool:
        query = users.update().where(users.c.id == data.id)
        query = query.values(
            {
                "recovery_code": data.code.get_secret_value(),
                "recovery_code_lifetime_end": data.expires,
            }
        )
        return bool(await self.session.execute(query))

    async def change_password(self, data: ChangePasswordDto) -> bool:
        query = users.update().where(users.c.id == data.id)
        query = query.where(users.c.password == data.hashed_old_password)

        if data.hashed_new_password is None:
            raise ValueError("hashed_new_password is None")
        query = query.values(
            {
                "password": data.hashed_new_password.get_secret_value(),
                "recovery_code": None,
                "recovery_code_lifetime_end": None,
            }
        )
        return bool(await self.session.execute(query))

    async def change_password_by_reset_code(
        self,
        data: ChangePasswordByResetCodeDto,
    ) -> bool:
        query = users.update().where(users.c.id == data.id)
        query = query.where(users.c.recovery_code == data.code)
        query = query.where(
            users.c.recovery_code_lifetime_end > datetime.now()
        )
        if data.hashed_new_password is None:
            raise ValueError("hashed_new_password is None")
        query = query.values(
            {
                "password": data.hashed_new_password.get_secret_value(),
                "recovery_code": None,
                "recovery_code_lifetime_end": None,
            }
        )
        return bool(await self.session.execute(query))
