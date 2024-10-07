from collections.abc import AsyncGenerator, Generator

import pytest
from faker import Faker
from httpx import ASGITransport, AsyncClient

from edm_su_api.internal.controller.http import app
from edm_su_api.internal.controller.http.v1.dependencies.auth import (
    get_current_user,
)
from edm_su_api.internal.entity.user import (
    User,
)
from edm_su_api.internal.entity.video import Video


@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        base_url="http://test",
        transport=ASGITransport(app=app),
    ) as client:
        yield client


@pytest.fixture
def mock_current_user(
    user: User,
) -> None:
    app.dependency_overrides[get_current_user] = lambda: user


@pytest.fixture(autouse=True)
def mock_clean_dependencies() -> Generator:
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def user_auth_headers(user: User) -> dict[str, str]:
    return {
        "X-User": str(user.id),
    }


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
