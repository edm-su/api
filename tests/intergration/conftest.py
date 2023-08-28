from collections.abc import AsyncGenerator

import pytest
from faker import Faker
from meilisearch_python_async import Client as MeilisearchClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.internal.entity.video import NewVideoDto, Video
from app.internal.usecase.repository.video import PostgresVideoRepository
from app.pkg.meilisearch import config_ms
from app.pkg.meilisearch import ms_client as meilisearch_client
from app.pkg.postgres import Base, async_engine, async_session


@pytest.fixture(autouse=True, scope="session")
async def _setup_db() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session")
async def pg_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session, session.begin():
        yield session


@pytest.fixture(scope="session")
async def ms_client() -> MeilisearchClient:
    await config_ms(meilisearch_client)
    return meilisearch_client


@pytest.fixture()
def pg_video_repository(
    pg_session: AsyncSession,
) -> PostgresVideoRepository:
    return PostgresVideoRepository(pg_session)


@pytest.fixture()
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
