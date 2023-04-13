from collections.abc import AsyncGenerator

import pytest
from faker import Faker
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.helpers import get_password_hash
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
from app.pkg.postgres import async_session


@pytest.fixture(scope="session")
async def pg_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

@pytest.fixture(autouse=True)
async def _pg_rollback(
    pg_session: AsyncSession,
) -> None:
    await pg_session.rollback()


@pytest.fixture(scope="session")
async def postgres_user_repository(
    pg_session: AsyncSession,
) -> PostgresUserRepository:
    return PostgresUserRepository(pg_session)


@pytest.fixture()
def new_user_data(faker: Faker) -> NewUserDto:
    password = faker.password()
    return NewUserDto(
        email=faker.email(),
        username=faker.user_name(),
        password=password,
        hashed_password=SecretStr(get_password_hash(password)),
        is_active=True,
        activation_code=SecretStr("test123"),
    )


@pytest.fixture()
async def pg_user(
    postgres_user_repository:PostgresUserRepository,
    new_user_data: NewUserDto,
) -> User:
    return await postgres_user_repository.create(new_user_data)

@pytest.fixture()
async def pg_nonactive_user(
    postgres_user_repository:PostgresUserRepository,
    new_user_data: NewUserDto,
) -> User:
    new_user_data.is_active = False
    return await postgres_user_repository.create(new_user_data)

@pytest.fixture()
async def pg_reset_user(
    postgres_user_repository:PostgresUserRepository,
    reset_password_data: ResetPasswordDto,
) -> bool:
    return await postgres_user_repository.set_reset_password_code(
        reset_password_data,
    )

@pytest.fixture()
def activate_user_data(pg_nonactive_user: User) -> ActivateUserDto:
    if pg_nonactive_user.activation_code is None:
        message = "Activation code is None"
        raise ValueError(message)
    return ActivateUserDto(
        id = pg_nonactive_user.id,
        activation_code=pg_nonactive_user.activation_code,
    )

@pytest.fixture()
def reset_password_data(
    pg_user: User,
    faker: Faker,
) -> ResetPasswordDto:
    return ResetPasswordDto(
        id = pg_user.id,
        code = SecretStr(faker.pystr(max_chars=10)),
        expires=faker.date_time_between(
            start_date="now",
            end_date="+1y",
        ),
    )

@pytest.fixture()
def change_password_data(
    pg_user: User,
    faker: Faker,
    new_user_data: NewUserDto,
) -> ChangePasswordDto:
    new_password = faker.password()
    return ChangePasswordDto(
        id = pg_user.id,
        old_password=new_user_data.password,
        new_password=SecretStr(new_password),
        hashed_old_password=pg_user.hashed_password,
        hashed_new_password=SecretStr(get_password_hash(new_password)),
    )

@pytest.fixture()
def change_password_with_code_data(
    pg_user: User,
    faker: Faker,
    reset_password_data: ResetPasswordDto,
) -> ChangePasswordByResetCodeDto:
    password = faker.password()
    return ChangePasswordByResetCodeDto(
        id = pg_user.id,
        code=reset_password_data.code,
        new_password=SecretStr(password),
        hashed_new_password=SecretStr(get_password_hash(password)),
    )

@pytest.fixture()
def sign_in_data(
    pg_user: User,
    new_user_data: NewUserDto,
) -> SignInDto:
    return SignInDto(
        email=pg_user.email,
        hashed_password = pg_user.hashed_password,
        password=new_user_data.password,
    )
