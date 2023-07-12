import json
import secrets
import string
from datetime import datetime, timedelta

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from pydantic import SecretStr
from typing_extensions import Self

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
    WrongResetCodeError,
)
from app.internal.usecase.repository.user import AbstractUserRepository
from app.pkg.nats import NatsClient


class AbstractUserUseCase:
    def __init__(
        self: Self,
        repository: AbstractUserRepository,
        broker: NatsClient,
    ) -> None:
        self.repository = repository
        self.broker = broker


def generate_secret_code(n: int = 10) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for i in range(n))


def verify_password(password: str, hashed_password: str) -> None:
    ph = PasswordHasher()
    try:
        ph.verify(hashed_password, password)
    except VerifyMismatchError as e:
        raise WrongPasswordError from e


class CreateUserUseCase(AbstractUserUseCase):
    async def execute(
        self: Self,
        new_user: NewUserDto,
    ) -> User:
        try:
            await self.repository.get_by_email(new_user.email)
        except UserNotFoundError:
            pass
        else:
            raise UserAlreadyExistsError(key="email")

        try:
            await self.repository.get_by_username(new_user.username)
        except UserNotFoundError:
            pass
        else:
            raise UserAlreadyExistsError(key="username")

        new_user.activation_code = SecretStr(generate_secret_code())

        user = await self.repository.create(new_user)

        broker_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "activation_code": new_user.activation_code.get_secret_value(),
        }
        await self.broker.publish(
            "USERS.created",
            json.dumps(broker_data).encode(),
        )

        return user


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
    async def execute(
        self: Self,
        email: str,
    ) -> None:
        user = await self.repository.get_by_email(email)

        data = ResetPasswordDto(
            id=user.id,
            code=SecretStr(generate_secret_code()),
            expires=datetime.now() + timedelta(hours=24),
        )

        await self.repository.set_reset_password_code(data)

        broker_data = {
            "id": user.id,
            "code": data.code.get_secret_value(),
            "email": user.email,
        }
        await self.broker.publish(
            "USERS.reset_password",
            json.dumps(broker_data).encode(),
        )


class ChangePasswordUseCase(AbstractUserUseCase):
    async def execute(
        self: Self,
        data: ChangePasswordDto,
    ) -> None:
        user = await self.repository.get_by_id(data.user_id)

        verify_password(
            data.old_password.get_secret_value(),
            user.hashed_password.get_secret_value(),
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
        try:
            await self.repository.change_password_by_reset_code(data)
        except UserNotFoundError as e:
            raise WrongResetCodeError from e


class SignInUseCase(AbstractUserUseCase):
    async def execute(
        self: Self,
        data: SignInDto,
    ) -> User:
        user = await self.repository.get_by_email(data.email)

        if not user.hashed_password:
            raise WrongPasswordError

        if user.is_banned:
            raise UserIsBannedError

        if not user.is_active:
            raise UserIsNotActivatedError
        verify_password(
            data.password.get_secret_value(),
            user.hashed_password.get_secret_value(),
        )

        return user
