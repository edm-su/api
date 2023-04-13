import asyncio
from collections.abc import Generator

import pytest
from faker import Faker


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def faker() -> Faker:
    return Faker()
