import pytest
from pydantic import SecretStr
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
        await postgres_user_repository.activate(activate_user_data)

        user = await postgres_user_repository.get_by_id(
            pg_nonactive_user.id,
        )
        assert user
        assert user.is_active

    async def test_change_password(
        self: Self,
        postgres_user_repository: PostgresUserRepository,
        change_password_data: ChangePasswordDto,
    ) -> None:
        await postgres_user_repository.change_password(
            change_password_data,
        )

        user = await postgres_user_repository.get_by_id(
            change_password_data.id,
        )
        assert user.hashed_password == change_password_data.hashed_new_password

    async def test_set_reset_password_code(
        self: Self,
        postgres_user_repository: PostgresUserRepository,
        reset_password_data: ResetPasswordDto,
    ) -> None:
        await postgres_user_repository.set_reset_password_code(
            reset_password_data,
        )

    async def test_change_password_by_reset_code(
        self: Self,
        postgres_user_repository: PostgresUserRepository,
        change_password_with_code_data: ChangePasswordByResetCodeDto,
        reset_password_data: ResetPasswordDto,
    ) -> None:
        await postgres_user_repository.set_reset_password_code(
            reset_password_data,
        )
        await postgres_user_repository.change_password_by_reset_code(
            change_password_with_code_data,
        )

        user = await postgres_user_repository.get_by_id(
            change_password_with_code_data.id,
        )
        assert (
            user.hashed_password
            == change_password_with_code_data.hashed_new_password
        )


class TestPostgresUserRepositoryBoundary:
    async def test_get_by_invalid_email(
        self: Self,
        postgres_user_repository: PostgresUserRepository,
        pg_user: User,
    ) -> None:
        fake_email = f"fake+${pg_user.email}"
        with pytest.raises(UserNotFoundError):
            await postgres_user_repository.get_by_email(fake_email)

    async def test_get_by_invalid_username(
        self: Self,
        postgres_user_repository: PostgresUserRepository,
        pg_user: User,
    ) -> None:
        fake_username = f"fake+${pg_user.username}"
        with pytest.raises(UserNotFoundError):
            await postgres_user_repository.get_by_username(fake_username)

    async def test_get_by_invalid_id(
        self: Self,
        postgres_user_repository: PostgresUserRepository,
        pg_user: User,
    ) -> None:
        fake_id = 1_000 + pg_user.id
        with pytest.raises(UserNotFoundError):
            await postgres_user_repository.get_by_id(fake_id)

    async def test_activate_with_wrong_code(
        self: Self,
        postgres_user_repository: PostgresUserRepository,
        activate_user_data: ActivateUserDto,
    ) -> None:
        activate_user_data.activation_code = "wrongcode"
        with pytest.raises(UserNotFoundError):
            await postgres_user_repository.activate(activate_user_data)

    async def test_change_password_with_wrong_reset_code(
        self: Self,
        postgres_user_repository: PostgresUserRepository,
        change_password_with_code_data: ChangePasswordByResetCodeDto,
    ) -> None:
        change_password_with_code_data.code = SecretStr("wrongcode")

        with pytest.raises(UserNotFoundError):
            await postgres_user_repository.change_password_by_reset_code(
                change_password_with_code_data,
            )

    async def test_change_password_with_wrong_user_id(
        self: Self,
        postgres_user_repository: PostgresUserRepository,
        change_password_data: ChangePasswordDto,
    ) -> None:
        change_password_data.id = change_password_data.id + 1_000

        with pytest.raises(UserNotFoundError):
            await postgres_user_repository.change_password(
                change_password_data,
            )

    async def test_create_without_hashed_password(
        self: Self,
        postgres_user_repository: PostgresUserRepository,
        new_user_data: NewUserDto,
    ) -> None:
        new_user_data.hashed_password = None

        with pytest.raises(HashedPasswordRequiredError):
            await postgres_user_repository.create(new_user_data)

    async def test_change_password_without_hashed_new_password(
        self: Self,
        postgres_user_repository: PostgresUserRepository,
        change_password_data: ChangePasswordDto,
    ) -> None:
        change_password_data.hashed_new_password = None
        with pytest.raises(ValueError):  # noqa: PT011
            await postgres_user_repository.change_password(
                change_password_data,
            )

    async def test_change_password_by_reset_code_without_hashed_new_password(
        self: Self,
        postgres_user_repository: PostgresUserRepository,
        change_password_with_code_data: ChangePasswordByResetCodeDto,
    ) -> None:
        change_password_with_code_data.hashed_new_password = None
        with pytest.raises(HashedPasswordRequiredError):
            await postgres_user_repository.change_password_by_reset_code(
                change_password_with_code_data,
            )

    async def test_set_reset_password_code_for_invalid_user(
        self: Self,
        postgres_user_repository: PostgresUserRepository,
        reset_password_data: ResetPasswordDto,
    ) -> None:
        reset_password_data.id = 999_999
        with pytest.raises(UserNotFoundError):
            await postgres_user_repository.set_reset_password_code(
                reset_password_data,
            )
