from abc import ABC
from datetime import datetime, timedelta

from pydantic import SecretStr

from app.helpers import generate_secret_code, get_password_hash
from app.internal.entity.user import (
    ActivateUserDto,
    ChangePasswordByResetCodeDto,
    ChangePasswordDto,
    NewUserDto,
    ResetPasswordDto,
    User,
)
from app.internal.usecase.exceptions.user import (
    UserAlreadyExistsException,
    UserNotFoundException,
    WrongActivationCodeException,
    WrongPasswordException,
    WrongResetCodeException,
)
from app.internal.usecase.repository.user import AbstractUserRepository


class AbstractUserUseCase(ABC):
    def __init__(
        self,
        repository: AbstractUserRepository,
    ) -> None:
        self.repository = repository


class CreateUserUseCase(AbstractUserUseCase):
    async def execute(self, new_user: NewUserDto) -> User:
        if await self.repository.get_by_email(new_user.email):
            raise UserAlreadyExistsException("email")
        if await self.repository.get_by_username(new_user.username):
            raise UserAlreadyExistsException("username", new_user.username)

        new_user.hashed_password = SecretStr(
            get_password_hash(new_user.password.get_secret_value())
        )
        new_user.activation_code = SecretStr(generate_secret_code())

        return await self.repository.create(new_user)


class ActivateUserUseCase(AbstractUserUseCase):
    async def execute(self, code: ActivateUserDto) -> bool:
        activated = await self.repository.activate(code)
        if not activated:
            raise WrongActivationCodeException()
        return activated


class GetUserByUsernameUseCase(AbstractUserUseCase):
    async def execute(self, username: str) -> User:
        user = await self.repository.get_by_username(username)
        if not user:
            raise UserNotFoundException("username", username)
        return user


class GetUserByIdUseCase(AbstractUserUseCase):
    async def execute(self, user_id: int) -> User:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException("id", user_id)
        return user


class ResetPasswordUseCase(AbstractUserUseCase):
    # TODO: после выноса отправки почты в отдельное приложение,
    # сделать возврат bool
    async def execute(self, email: str) -> ResetPasswordDto:
        user = await self.repository.get_by_email(email)
        if not user:
            raise UserNotFoundException("email", email)

        data = ResetPasswordDto(
            id=user.id,
            code=SecretStr(generate_secret_code()),
            expires=datetime.now() + timedelta(hours=1),
        )

        if not await self.repository.set_reset_password_code(data):
            raise UserNotFoundException("email", email)
        return data


class ChangePasswordUseCase(AbstractUserUseCase):
    async def execute(self, data: ChangePasswordDto) -> bool:
        data.hashed_old_password = SecretStr(
            get_password_hash(data.old_password.get_secret_value())
        )

        data.hashed_new_password = SecretStr(
            get_password_hash(data.new_password.get_secret_value())
        )

        if not await self.repository.change_password(data):
            raise WrongPasswordException()

        return True


class ChangePasswordByResetCodeUseCase(AbstractUserUseCase):
    async def execute(self, data: ChangePasswordByResetCodeDto) -> bool:
        user = await self.repository.get_by_id(data.id)
        if not user:
            raise UserNotFoundException("id", data.id)

        data.hashed_new_password = SecretStr(
            get_password_hash(data.new_password.get_secret_value())
        )

        if not await self.repository.change_password_by_reset_code(data):
            raise WrongResetCodeException()

        return True
