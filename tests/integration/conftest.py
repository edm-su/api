from collections.abc import AsyncGenerator

import pytest
from faker import Faker
from meilisearch_python_async import Client as MeilisearchClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from edm_su_api.internal.entity.video import NewVideoDto, Video
from edm_su_api.internal.usecase.repository.video import (
    PostgresVideoRepository,
)
from edm_su_api.pkg import postgres
from edm_su_api.pkg.meilisearch import config_ms
from edm_su_api.pkg.meilisearch import ms_client as meilisearch_client


@pytest.fixture(autouse=True, scope="session")
async def setup_db() -> None:
    session_mpatch = pytest.MonkeyPatch()

    engine = postgres.new_async_engine()

    session_mpatch.setattr(postgres, "_ASYNC_ENGINE", engine)
    session_mpatch.setattr(
        postgres,
        "_ASYNC_SESSIONMAKER",
        async_sessionmaker(engine, expire_on_commit=False),
    )

    async with engine.begin() as conn:
        await conn.run_sync(postgres.Base.metadata.drop_all)
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
        await conn.run_sync(postgres.Base.metadata.create_all)


@pytest.fixture(name="pg_session")
async def session_with_rollback(
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncGenerator[AsyncSession, None]:
    connection = await postgres._ASYNC_ENGINE.connect()  # noqa: SLF001
    transaction = await connection.begin()

    session = AsyncSession(bind=connection, expire_on_commit=False)

    monkeypatch.setattr(postgres, "get_async_session", lambda: session)

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()


@pytest.fixture(scope="session")
async def ms_client() -> MeilisearchClient:
    await config_ms(meilisearch_client)
    return meilisearch_client


@pytest.fixture(scope="session")
async def pg_video_repository(
    pg_session: AsyncSession,
) -> PostgresVideoRepository:
    return PostgresVideoRepository(pg_session)


@pytest.fixture(scope="session")
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
