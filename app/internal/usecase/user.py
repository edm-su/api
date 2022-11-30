from abc import ABC

from app.helpers import get_password_hash
from app.internal.usecase.exceptions.user import (
    UserAlreadyExistsException,
    UserNotFoundException,
    WrongActivationCodeException,
)
from app.internal.usecase.repository.user import AbstractUserRepository
from app.schemas.user import CreateUser, MyUser, NewUserDto, User


class AbstractUserUseCase(ABC):
    def __init__(
        self,
        repository: AbstractUserRepository,
    ) -> None:
        self.repository = repository


class CreateUserUseCase(AbstractUserUseCase):
    async def execute(self, new_user: CreateUser) -> User:
        if await self.repository.get_by_email(new_user.email):
            raise UserAlreadyExistsException("email")
        if await self.repository.get_by_username(new_user.username):
            raise UserAlreadyExistsException("username", new_user.username)

        return await self.repository.create(
            NewUserDto(
                username=new_user.username,
                email=new_user.email,
                password=get_password_hash(new_user.password),
            )
        )


class ActivateUserUseCase(AbstractUserUseCase):
    async def execute(self, code: str) -> bool:
        activated = await self.repository.activate(code)
        if not activated:
            raise WrongActivationCodeException()
        return activated


class GetUserByUsernameUseCase(AbstractUserUseCase):
    async def execute(self, username: str) -> MyUser:
        user = await self.repository.get_by_username(username)
        if not user:
            raise UserNotFoundException("username", username)
        return user


class GetUserByIdUseCase(AbstractUserUseCase):
    async def execute(self, user_id: int) -> User:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException("id", user_id)
        return User(**user.dict())
