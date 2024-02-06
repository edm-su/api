import asyncio
from collections.abc import Generator
from io import BytesIO
from typing import IO

import pytest
from faker import Faker
from PIL import Image

from app.internal.entity.user import User


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def faker() -> Faker:
    return Faker()


@pytest.fixture(scope="session")
def user(faker: Faker) -> User:
    return User(id=faker.uuid4())


@pytest.fixture()
def image() -> IO[bytes]:
    buf = BytesIO()
    Image.new("RGB", (60, 60), "red").save(buf, "JPEG")
    return buf
