import time
import typing
from asyncio import AbstractEventLoop, get_event_loop
from contextlib import suppress
from datetime import datetime, timedelta

import pytest
from _pytest.monkeypatch import MonkeyPatch
from faker import Faker
from httpx import AsyncClient
from meilisearch_python_async.task import wait_for_task
from sqlalchemy import create_engine, event
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app import helpers, tasks
from app.crud import dj as djs_crud
from app.crud import livestream as livestream_crud
from app.crud import post as post_crud
from app.crud import token as tokens_crud
from app.crud import user as user_crud
from app.db import database, metadata
from app.internal.entity.post import BasePost
from app.internal.usecase.repository.video import PostgresVideoRepository
from app.main import app
from app.meilisearch import (
    config_ms,
    ms_client,
)
from app.pkg.postgres import get_session
from app.repositories.user_video import PostgresUserVideoRepository
from app.schemas.dj import CreateDJ
from app.schemas.livestreams import CreateLiveStream
from app.schemas.user import CreateUser, User
from app.schemas.video import CreateVideo, PgVideo
from app.settings import settings


@pytest.fixture(scope="session")
async def client() -> typing.AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="session")
def _setup_db() -> typing.Generator:
    engine = create_engine(settings.database_url.replace("+asyncpg", ""))
    conn = engine.connect()
    conn.execute("commit")
    try:
        conn.execute("drop database test")
    except SQLAlchemyError:
        pass
    finally:
        conn.close()

    conn = engine.connect()
    conn.execute("commit")
    conn.execute("create database test")
    conn.close()

    yield

    conn = engine.connect()
    conn.execute("commit")
    with suppress(SQLAlchemyError):
        conn.execute("drop database test")
    conn.close()


@pytest.fixture(scope="session", autouse=True)
def _setup_test_db(setup_db: typing.Generator) -> typing.Generator:
    engine = create_engine(settings.database_url.replace("+asyncpg", ""))

    with engine.begin():
        metadata.drop_all(engine)
        metadata.create_all(engine)
        yield
        metadata.drop_all(engine)


@pytest.fixture()
async def pg_session() -> typing.AsyncGenerator:
    async_engine = create_async_engine(settings.database_url)
    async with async_engine.connect() as conn:
        await conn.begin()
        await conn.begin_nested()
        AsyncSessionLocal = sessionmaker(  # noqa: N806
            autocommit=False,
            autoflush=False,
            bind=conn,
            future=True,
            class_=AsyncSession,
        )

        async_session: AsyncSession = AsyncSessionLocal()  # type: ignore[valid-type]  # noqa: E501

        @event.listens_for(async_session.sync_session, "after_transaction_end")
        def end_savepoint(
            session: AsyncSession,
            **kwargs: dict[str, typing.Any],
        ) -> None:
            if conn.closed:
                return
            if not conn.in_nested_transaction:
                conn.sync_connection.begin_nested()

        def test_get_session() -> typing.Generator:
            with suppress(SQLAlchemyError):
                yield AsyncSessionLocal

        app.dependency_overrides[get_session] = test_get_session

        yield async_session
        await async_session.close()
        await conn.rollback()


@pytest.fixture(autouse=True)
async def _db_connect() -> typing.AsyncGenerator[None, None]:
    await database.connect()
    yield
    await database.disconnect()


@pytest.fixture(autouse=True, scope="session")
async def _configure_meilisearch() -> None:
    await config_ms(ms_client)


@pytest.fixture(scope="session")
def event_loop() -> AbstractEventLoop:
    return get_event_loop()


@pytest.fixture(scope="session", autouse=True)
async def _clear_meilisearch() -> typing.AsyncGenerator[None, None]:
    await remove_meilisearch_indexes()
    yield
    await remove_meilisearch_indexes()


async def remove_meilisearch_indexes() -> None:
    indexes = await ms_client.get_indexes()
    if indexes:
        clear_indexes = [
            index
            for index in indexes
            if index.uid.endswith(settings.meilisearch_index_postfix)
        ]

        for index in clear_indexes:
            task = await index.delete_all_documents()
            await wait_for_task(
                ms_client.http_client,
                task.task_uid,
            )


@pytest.fixture(scope="session")
def pg_user_video_repository() -> PostgresUserVideoRepository:
    return PostgresUserVideoRepository(database)


@pytest.fixture()
async def video_data(faker: Faker) -> dict:
    title = faker.sentence(nb_words=3)
    return {
        "title": title,
        "date": faker.date(),
        "yt_id": faker.domain_word(),
        "yt_thumbnail": faker.image_url(),
        "duration": faker.pyint(min_value=1200, max_value=12000),
    }


@pytest.fixture()
async def pg_video(
    video_data: dict,
    pg_video_repository: PostgresVideoRepository,
) -> PgVideo:
    return await pg_video_repository.create(CreateVideo(**video_data))


@pytest.fixture()
async def videos(
    faker: Faker,
    pg_video_repository: PostgresVideoRepository,
) -> list[PgVideo]:
    videos_list = [
        CreateVideo(
            title=faker.name(),
            slug=faker.slug(),
            date=faker.date(),
            yt_id=faker.pystr(min_chars=11, max_chars=11),
            yt_thumbnail=faker.url() + faker.file_path(extension="jpg"),
            duration=faker.pyint(min_value=1200),
        )
        for _ in range(3)
    ]
    return [await pg_video_repository.create(video) for video in videos_list]


@pytest.fixture()
async def posts(
    admin: typing.Mapping,
    faker: Faker,
) -> list[None | typing.Mapping]:
    post = BasePost(
        title=faker.name(),
        text={
            "time": int(time.time()),
            "blocks": [{"type": "paragraph", "data": {"text": "test"}}],
            "version": "2.19.0",
        },
        slug=faker.slug(),
        published_at=datetime.now(),
    )
    return [await post_crud.create_post(post, admin["id"])]


@pytest.fixture()
async def liked_video(
    admin: typing.Mapping,
    pg_video: PgVideo,
    pg_user_video_repository: PostgresUserVideoRepository,
) -> PgVideo:
    user = User(**admin)
    await pg_user_video_repository.like_video(user, pg_video)
    return pg_video


@pytest.fixture()
async def user_data(faker: Faker) -> CreateUser:
    password = faker.password()
    return CreateUser(
        username=faker.user_name(),
        email=faker.email(),
        password=password,
        password_confirm=password,
    )


@pytest.fixture()
async def admin(user_data: CreateUser) -> None | typing.Mapping:
    return await user_crud.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        is_admin=True,
    )


@pytest.fixture()
async def non_activated_user(user_data: CreateUser) -> None | typing.Mapping:
    return await user_crud.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
    )


@pytest.fixture()
async def user(user_data: CreateUser) -> None | typing.Mapping:
    return await user_crud.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        is_active=True,
    )


@pytest.fixture()
async def channel_data(faker: Faker) -> dict:
    return {
        "name": faker.name(),
        "yt_id": faker.pystr(min_chars=11, max_chars=11),
        "yt_thumbnail": faker.url() + faker.file_path(extension="jpg"),
    }


@pytest.fixture()
async def recovered_user_code(admin: dict) -> str:
    return await user_crud.generate_recovery_user_code(admin["id"])


@pytest.fixture(autouse=True)
def _no_send_email(monkeypatch: MonkeyPatch) -> None:
    def mock_send_email(*args: list, **kwargs: dict) -> None:
        pass

    monkeypatch.setattr(tasks, "send_email", mock_send_email)


@pytest.fixture()
def livestream_data(faker: Faker) -> CreateLiveStream:
    start_time: datetime = faker.future_datetime()
    end_time = start_time + timedelta(hours=2)
    return CreateLiveStream(
        title=faker.company(),
        start_time=start_time,
        end_time=end_time,
        image=faker.file_path(extension="jpg"),
        genres=[faker.name() for _ in range(2)],
        url=faker.uri(),
        djs=[faker.name() for _ in range(2)],
    )


@pytest.fixture()
async def livestream(
    livestream_data: CreateLiveStream,
) -> None | typing.Mapping:
    return await livestream_crud.create(livestream_data)


@pytest.fixture()
async def livestream_in_a_month(
    livestream_data: CreateLiveStream,
) -> None | typing.Mapping:
    start_time = datetime.now() + timedelta(days=32)
    livestream_data.start_time = start_time
    livestream_data.end_time = start_time + timedelta(hours=2)
    return await livestream_crud.create(livestream_data)


@pytest.fixture()
def dj_data(faker: Faker) -> CreateDJ:
    return CreateDJ(
        name=faker.name(),
        real_name=faker.name(),
        aliases=[faker.name() for _ in range(3)],
        country=faker.country(),
        genres=[faker.name() for _ in range(2)],
        image=faker.file_path(extension="jpg"),
        birth_date=faker.date(),
        site=faker.url(),
    )


@pytest.fixture()
async def dj(dj_data: CreateDJ) -> None | typing.Mapping:
    return await djs_crud.create(dj_data)


@pytest.fixture()
def group_data(
    faker: Faker,
    dj: typing.Mapping,
    dj_data: CreateDJ,
) -> CreateDJ:
    dj_data.name = faker.name()
    dj_data.slug = faker.slug()
    dj_data.is_group = True
    dj_data.group_members = [dj["id"]]
    return dj_data


@pytest.fixture()
async def group(group_data: CreateDJ) -> typing.Mapping:
    return await djs_crud.create(group_data)


@pytest.fixture()
async def api_token(admin: typing.Mapping, faker: Faker) -> str:
    token = helpers.generate_token()
    await tokens_crud.add_token(faker.name(), token, admin["id"])
    return token
