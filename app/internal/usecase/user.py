from datetime import datetime, timedelta

from pydantic import SecretStr
from typing_extensions import Self

from app.helpers import generate_secret_code, get_password_hash
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
    UserNotActivatedError,
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
    ) -> bool:
        activated = await self.repository.activate(code)
        if not activated:
            raise WrongActivationCodeError
        return activated


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
        if not user:
            raise UserNotFoundError

        data = ResetPasswordDto(
            id=user.id,
            code=SecretStr(generate_secret_code()),
            expires=datetime.now() + timedelta(hours=1),
        )

        if not await self.repository.set_reset_password_code(data):
            raise UserNotFoundError
        return data


class ChangePasswordUseCase(AbstractUserUseCase):
    async def execute(
        self: Self,
        data: ChangePasswordDto,
    ) -> bool:
        data.hashed_old_password = SecretStr(
            get_password_hash(data.old_password.get_secret_value()),
        )

        data.hashed_new_password = SecretStr(
            get_password_hash(data.new_password.get_secret_value()),
        )

        if not await self.repository.change_password(data):
            raise WrongPasswordError

        return True


class ChangePasswordByResetCodeUseCase(AbstractUserUseCase):
    async def execute(
        self: Self,
        data: ChangePasswordByResetCodeDto,
    ) -> bool:
        user = await self.repository.get_by_id(data.id)
        if not user:
            raise UserNotFoundError

        data.hashed_new_password = SecretStr(
            get_password_hash(data.new_password.get_secret_value()),
        )

        if not await self.repository.change_password_by_reset_code(data):
            raise WrongResetCodeError

        return True


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
            raise UserNotActivatedError

        return user
