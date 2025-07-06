from collections.abc import AsyncGenerator

import pytest
from faker import Faker
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    AsyncTransaction,
)

from edm_su_api.internal.entity.video import NewVideoDto, Video
from edm_su_api.internal.usecase.repository.video import (
    PostgresVideoRepository,
)
from edm_su_api.pkg.postgres import async_engine


@pytest.fixture(autouse=True, scope="session")
async def pg_connection() -> AsyncGenerator[AsyncConnection, None]:
    async with async_engine.connect() as connection:
        yield connection


@pytest.fixture
async def pg_transaction(
    pg_connection: AsyncConnection,
) -> AsyncGenerator[AsyncTransaction, None]:
    async with pg_connection.begin() as transaction:
        yield transaction


@pytest.fixture
async def pg_session(
    pg_connection: AsyncConnection,
    pg_transaction: AsyncTransaction,
) -> AsyncGenerator[AsyncSession, None]:
    async_session = AsyncSession(
        bind=pg_connection,
        join_transaction_mode="create_savepoint",
    )

    yield async_session

    await pg_transaction.rollback()


@pytest.fixture
def pg_video_repository(
    pg_session: AsyncSession,
) -> PostgresVideoRepository:
    return PostgresVideoRepository(pg_session)


@pytest.fixture
async def pg_video(
    pg_video_repository: PostgresVideoRepository,
    faker: Faker,
) -> Video:
    video = NewVideoDto(
        title=faker.word(),
        date=faker.date_between(
            start_date="-1y",
            end_date="now",
        ),
        yt_id=faker.uuid4(),
        yt_thumbnail=faker.url(),
        duration=faker.pyint(),
        slug=faker.slug(),
    )
    return await pg_video_repository.create(video)
