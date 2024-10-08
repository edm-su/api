from io import BytesIO
from typing import IO

import pytest
from faker import Faker
from PIL import Image

from edm_su_api.internal.entity.user import User


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
def faker() -> Faker:
    return Faker()


@pytest.fixture(scope="session")
def user(faker: Faker) -> User:
    return User(id=faker.uuid4())


@pytest.fixture
def image() -> IO[bytes]:
    buf = BytesIO()
    Image.new("RGB", (60, 60), "red").save(buf, "JPEG")
    return buf
