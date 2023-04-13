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
from app.internal.usecase.repository.user import PostgresUserRepository


class TestPostgresUserRepository:
    async def test_get_by_email(
        self: Self,
        postgres_user_repository: PostgresUserRepository,
        pg_user: User,
    ) -> None:
        result = await postgres_user_repository.get_by_email(pg_user.email)
        assert result == pg_user

    async def test_get_by_username(
        self: Self,
        postgres_user_repository: PostgresUserRepository,
        pg_user: User,
    ) -> None:
        result = await postgres_user_repository.get_by_username(
            pg_user.username,
        )
        assert result == pg_user

    async def test_get_by_id(
        self: Self,
        postgres_user_repository: PostgresUserRepository,
        pg_user: User,
    ) -> None:
        result = await postgres_user_repository.get_by_id(pg_user.id)
        assert result == pg_user

    async def test_create(
        self: Self,
        postgres_user_repository: PostgresUserRepository,
        new_user_data: NewUserDto,
    ) -> None:
        result = await postgres_user_repository.create(new_user_data)
        assert isinstance(result, User)
        assert result.email == new_user_data.email

        assert result.username == new_user_data.username

    async def test_activate(
        self: Self,
        postgres_user_repository: PostgresUserRepository,
        activate_user_data: ActivateUserDto,
        pg_nonactive_user: User,
    ) -> None:
        result = await postgres_user_repository.activate(activate_user_data)
        assert result

        user = await postgres_user_repository.get_by_id(
            pg_nonactive_user.id,
        )
        assert user
        assert user.is_active

    async def test_set_reset_password_code(
        self: Self,
        postgres_user_repository: PostgresUserRepository,
        reset_password_data: ResetPasswordDto,
    ) -> None:
        result = await postgres_user_repository.set_reset_password_code(
            reset_password_data,
        )
        assert result

    async def test_change_password(
        self: Self,
        postgres_user_repository: PostgresUserRepository,
        change_password_data: ChangePasswordDto,
    ) -> None:
        result = await postgres_user_repository.change_password(
            change_password_data,
        )
        assert result

    async def test_change_password_by_reset_code(
        self: Self,
        postgres_user_repository: PostgresUserRepository,
        change_password_with_code_data: ChangePasswordByResetCodeDto,
        pg_reset_user: bool,  # noqa: FBT001
    ) -> None:
        result = await postgres_user_repository.change_password_by_reset_code(
            change_password_with_code_data,
        )
        assert result

    async def test_sign_in(
        self: Self,
        postgres_user_repository: PostgresUserRepository,
        sign_in_data: SignInDto,
        pg_user: User,
    ) -> None:
        result = await postgres_user_repository.sign_in(
            sign_in_data,
        )
        assert result
        assert isinstance(result, User)
        assert result.id == pg_user.id

class TestPostgresUserRepositoryBoundary():
    async def test_get_by_invalid_email(
        self: Self,
        postgres_user_repository: PostgresUserRepository,
        pg_user: User,
    ) -> None:
        fake_email = f"fake+${pg_user.email}"
        result = await postgres_user_repository.get_by_email(fake_email)
        assert result is None

    async def test_get_by_invalid_username(
        self: Self,
        postgres_user_repository: PostgresUserRepository,
        pg_user: User,
    ) -> None:
        fake_username = f"fake+${pg_user.username}"
        result = await postgres_user_repository.get_by_username(fake_username)
        assert result is None

    async def test_get_by_invalid_id(
        self: Self,
        postgres_user_repository: PostgresUserRepository,
        pg_user: User,
    ) -> None:
        fake_id = 1 + pg_user.id
        result = await postgres_user_repository.get_by_id(fake_id)
        assert result is None

    async def test_activate_with_wrong_code(
        self: Self,
        postgres_user_repository: PostgresUserRepository,
        activate_user_data: ActivateUserDto,
    ) -> None:
        activate_user_data.activation_code = SecretStr("wrongcode")
        result = await postgres_user_repository.activate(activate_user_data)
        assert result is False

    async def test_change_password_with_wrong_old_password(
        self: Self,
        postgres_user_repository: PostgresUserRepository,
        change_password_data: ChangePasswordDto,
    ) -> None:
        change_password_data.hashed_old_password = SecretStr("wrongpassword")
        result = await postgres_user_repository.change_password(
            change_password_data,
        )
        assert result is False

    async def test_change_password_with_wrong_reset_code(
        self: Self,
        pg_reset_user: bool,  # noqa: FBT001
        postgres_user_repository: PostgresUserRepository,
        change_password_with_code_data: ChangePasswordByResetCodeDto,
    ) -> None:
        change_password_with_code_data.code = SecretStr("wrongcode")
        result = await postgres_user_repository.change_password_by_reset_code(
            change_password_with_code_data,
        )
        assert result is False

    async def test_sign_in_with_wrong_password(
        self: Self,
        postgres_user_repository: PostgresUserRepository,
        sign_in_data: SignInDto,
    ) -> None:
        sign_in_data.hashed_password = SecretStr("wrongpassword")
        result = await postgres_user_repository.sign_in(
            sign_in_data,
        )
        assert result is None
