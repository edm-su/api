from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import users
from app.schemas.user import MyUser, NewUserDto, User


class AbstractUserRepository(ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> MyUser | None:
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> MyUser | None:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: int) -> MyUser | None:
        pass

    @abstractmethod
    async def create(self, user: NewUserDto) -> User:
        pass

    @abstractmethod
    async def activate(self, code: str) -> bool:
        pass


class PostgresUserRepository(AbstractUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def __get_by(self, whereclauses: list) -> MyUser | None:
        query = users.select()
        for whereclause in whereclauses:
            query = query.where(whereclause)

        result = await self.session.execute(query)
        result = result.first()
        return MyUser(**result) if result else None

    async def get_by_email(self, email: str) -> MyUser | None:
        return await self.__get_by([users.c.email == email])

    async def get_by_username(self, username: str) -> MyUser | None:
        return await self.__get_by([users.c.username == username])

    async def get_by_id(self, user_id: int) -> MyUser | None:
        return await self.__get_by([users.c.id == user_id])

    async def create(self, user: NewUserDto) -> User:
        query = users.insert().values(**user.dict())
        result = await self.session.execute(query)
        return User(
            id=result.inserted_primary_key[0],
            **user.dict(by_alias=True),
        )

    async def activate(self, code: str) -> bool:
        query = users.update().where(users.c.is_activate.is_(False))
        query = query.where(users.c.activation_code == code)
        query = query.values(is_activate=True, activation_code=None)
        return bool(await self.session.execute(query))
