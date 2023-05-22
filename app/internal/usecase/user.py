import hashlib
import secrets
import string
from datetime import datetime, timedelta

from pydantic import SecretStr
from typing_extensions import Self

from app.internal.entity.settings import settings
from app.internal.entity.user import (
    ActivateUserDto,
    ChangePasswordByResetCodeDto,
    ChangePasswordDto,
    NewUserDto,
    ResetPasswordDto,
    SignInDto,
    User,
)
from app.internal.usecase.exceptions.user import (
    UserAlreadyExistsError,
    UserIsBannedError,
    UserIsNotActivatedError,
    UserNotFoundError,
    WrongActivationCodeError,
    WrongPasswordError,
    WrongPasswordOrEmailError,
    WrongResetCodeError,
)
from app.internal.usecase.repository.user import AbstractUserRepository


class AbstractUserUseCase:
    def __init__(
        self: Self,
        repository: AbstractUserRepository,
    ) -> None:
        self.repository = repository


def generate_secret_code(n: int = 10) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for i in range(n))


def get_password_hash(password: str) -> str:
    encoded_password = f"{password}{settings.secret_key}".encode()
    return hashlib.sha256(encoded_password).hexdigest()


class CreateUserUseCase(AbstractUserUseCase):
    async def execute(
        self: Self,
        new_user: NewUserDto,
    ) -> User:
        if await self.repository.get_by_email(new_user.email):
            raise UserAlreadyExistsError(key="email")
        if await self.repository.get_by_username(new_user.username):
            raise UserAlreadyExistsError(
                key="username",
                value=new_user.username,
            )

        new_user.hashed_password = SecretStr(
            get_password_hash(new_user.password.get_secret_value()),
        )
        new_user.activation_code = SecretStr(generate_secret_code())

        return await self.repository.create(new_user)


class ActivateUserUseCase(AbstractUserUseCase):
    async def execute(
        self: Self,
        code: ActivateUserDto,
    ) -> None:
        try:
            await self.repository.activate(code)
        except UserNotFoundError as e:
            raise WrongActivationCodeError from e


class GetUserByUsernameUseCase(AbstractUserUseCase):
    async def execute(
        self: Self,
        username: str,
    ) -> User:
        user = await self.repository.get_by_username(username)
        if not user:
            raise UserNotFoundError
        return user


class GetUserByIdUseCase(AbstractUserUseCase):
    async def execute(
        self: Self,
        user_id: int,
    ) -> User:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError
        return user


class ResetPasswordUseCase(AbstractUserUseCase):
    # TODO: после выноса отправки почты в отдельное приложение,
    # сделать возврат bool
    async def execute(
        self: Self,
        email: str,
    ) -> ResetPasswordDto:
        user = await self.repository.get_by_email(email)

        data = ResetPasswordDto(
            id=user.id,
            code=SecretStr(generate_secret_code()),
            expires=datetime.now() + timedelta(hours=24),
        )

        await self.repository.set_reset_password_code(data)
        return data


class ChangePasswordUseCase(AbstractUserUseCase):
    async def execute(
        self: Self,
        data: ChangePasswordDto,
    ) -> None:
        data.hashed_old_password = SecretStr(
            get_password_hash(data.old_password.get_secret_value()),
        )

        data.hashed_new_password = SecretStr(
            get_password_hash(data.new_password.get_secret_value()),
        )

        try:
            await self.repository.change_password(data)
        except UserNotFoundError as e:
            raise WrongPasswordError from e


class ChangePasswordByResetCodeUseCase(AbstractUserUseCase):
    async def execute(
        self: Self,
        data: ChangePasswordByResetCodeDto,
    ) -> None:
        user = await self.repository.get_by_id(data.id)
        if not user:
            raise UserNotFoundError

        data.hashed_new_password = SecretStr(
            get_password_hash(data.new_password.get_secret_value()),
        )

        try:
            await self.repository.change_password_by_reset_code(data)
        except UserNotFoundError as e:
            raise WrongResetCodeError from e


class SignInUseCase(AbstractUserUseCase):
    async def execute(
        self: Self,
        data: SignInDto,
    ) -> User:
        data.hashed_password = SecretStr(
            get_password_hash(data.password.get_secret_value()),
        )

        user = await self.repository.sign_in(data)

        if not user:
            raise WrongPasswordOrEmailError

        if user.is_banned:
            raise UserIsBannedError

        if not user.is_active:
            raise UserIsNotActivatedError

        return user
