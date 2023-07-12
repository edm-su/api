from collections.abc import AsyncGenerator, Generator

import pytest
from faker import Faker
from httpx import AsyncClient
from pydantic import SecretStr

from app.internal.controller.http.v1.dependencies.auth import (
    get_current_admin,
    get_current_user,
)
from app.internal.entity.user import TokenData, User, get_password_hash
from app.internal.entity.video import Video
from app.main import app


@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture()
def _mock_current_user(
    user: User,
) -> None:
    app.dependency_overrides[get_current_user] = lambda: user


@pytest.fixture()
def _mock_current_admin(
    user: User,
) -> None:
    user.is_admin = True
    app.dependency_overrides[get_current_admin] = lambda: user


@pytest.fixture(autouse=True)
def _mock_clean_dependencies() -> Generator:
    yield
    app.dependency_overrides.clear()


@pytest.fixture()
def user(faker: Faker) -> User:
    return User(
        id=faker.random_int(min=1, max=1000),
        username=faker.user_name(),
        email=faker.email(),
        created=faker.date_time(),
        is_active=True,
        password=SecretStr(get_password_hash(faker.password())),
    )


@pytest.fixture()
def user_auth_headers(user: User) -> dict[str, str]:
    token = TokenData(
        id=user.id,
        email=user.email,
        username=user.username,
        is_admin=user.is_admin,
    )
    return {"Authorization": f"Bearer {token.access_token()}"}


@pytest.fixture(scope="session")
def video(faker: Faker) -> Video:
    return Video(
        id=faker.random_int(min=1, max=1000),
        title=faker.word(),
        date=faker.date(),
        yt_id=faker.word(),
        yt_thumbnail=faker.url(),
        duration=faker.random_int(min=1, max=1000),
        slug=faker.word(),
    )
