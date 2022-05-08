import typing
from asyncio import AbstractEventLoop, get_event_loop
from datetime import datetime, timedelta
from random import randint

import pytest
from _pytest.monkeypatch import MonkeyPatch
from faker import Faker
from httpx import AsyncClient
from meilisearch_python_async.task import wait_for_task

from app import tasks, helpers
from app.crud import dj as djs_crud
from app.crud import livestream as livestream_crud
from app.crud import post as post_crud
from app.crud import token as tokens_crud
from app.crud import user as user_crud
from app.crud import video as video_crud
from app.db import database
from app.main import app
from app.meilisearch import meilisearch_client
from app.repositories.video import meilisearch_video_repository
from app.schemas.dj import CreateDJ
from app.schemas.livestreams import CreateLiveStream
from app.schemas.post import BasePost
from app.schemas.user import CreateUser
from app.schemas.video import CreateVideo, MeilisearchVideo, Video
from app.settings import settings


@pytest.fixture(scope='session')
async def client() -> typing.AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test') as client:
        yield client


@pytest.fixture(autouse=True)
async def db_connect() -> typing.AsyncGenerator[None, None]:
    await database.connect()
    yield
    await database.disconnect()


@pytest.fixture(scope='session')
def event_loop() -> typing.Generator[AbstractEventLoop, None, None]:
    loop = get_event_loop()
    yield loop


@pytest.fixture(scope='session', autouse=True)
async def clear_meilisearch() -> None:
    await remove_meilisearch_indexes()
    yield
    await remove_meilisearch_indexes()


async def remove_meilisearch_indexes():
    indexes = await meilisearch_client.indexes()
    if indexes:
        clear_indexes = [
            index for index in indexes
            if index.uid.endswith(settings.meilisearch_index_postfix)
        ]
        for index in clear_indexes:
            task = await meilisearch_client.clear_index(index)
            await wait_for_task(
                meilisearch_client.client.http_client,
                task.uid
            )


@pytest.fixture
async def video_data(faker: Faker) -> dict:
    title = faker.sentence(nb_words=3)
    return {
        "title": title,
        "date": faker.date(),
        "yt_id": faker.domain_word(),
        "yt_thumbnail": faker.image_url(),
        "duration": randint(1200, 12000)
    }


@pytest.fixture
async def videos(faker: Faker) -> list[typing.Optional[typing.Mapping]]:
    videos_list = [CreateVideo(
        title=faker.name(),
        slug=faker.slug(),
        date=faker.date(),
        yt_id=faker.pystr(min_chars=11, max_chars=11),
        yt_thumbnail=faker.url() + faker.file_path(extension='jpg'),
        duration=faker.pyint(min_value=1200)
    ) for _ in range(3)]
    result = [await video_crud.add_video(video) for video in videos_list]
    return result


@pytest.fixture
async def posts(
        admin: typing.Mapping,
        faker: Faker,
) -> list[None | typing.Mapping]:
    post = BasePost(
        title=faker.name(),
        text={
            "time": datetime.now().timestamp(),
            "blocks": [{"type": "paragraph", "data": {"text": "test"}}],
            "version": "2.19.0",
        },
        slug=faker.slug(),
        published_at=datetime.now(),
    )
    return [await post_crud.create_post(post, admin['id'])]


@pytest.fixture
async def liked_video(
        admin: typing.Mapping,
        videos: typing.List[typing.Mapping],
) -> typing.Mapping:
    await video_crud.like_video(admin['id'], videos[0]['id'])
    return videos[0]


@pytest.fixture
async def user_data(faker: Faker) -> CreateUser:
    password = faker.password()
    return CreateUser(
        username=faker.user_name(),
        email=faker.email(),
        password=password,
        password_confirm=password
    )


@pytest.fixture
async def admin(user_data: CreateUser) -> None | typing.Mapping:
    return await user_crud.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        is_admin=True,
    )


@pytest.fixture
async def non_activated_user(user_data: CreateUser) -> None | typing.Mapping:
    return await user_crud.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
    )


@pytest.fixture
async def user(user_data: CreateUser) -> None | typing.Mapping:
    return await user_crud.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        is_active=True,
    )


@pytest.fixture
async def channel_data(faker: Faker) -> dict:
    return {
        'name': faker.name(),
        'yt_id': faker.pystr(min_chars=11, max_chars=11),
        'yt_thumbnail': faker.url() + faker.file_path(extension='jpg')
    }


@pytest.fixture
async def recovered_user_code(admin: dict) -> str:
    return await user_crud.generate_recovery_user_code(admin['id'])


@pytest.fixture(autouse=True)
def no_send_email(monkeypatch: MonkeyPatch) -> None:
    def mock_send_email(*args: list, **kwargs: dict) -> None:
        pass

    monkeypatch.setattr(tasks, 'send_email', mock_send_email)


@pytest.fixture
def livestream_data(faker: Faker) -> CreateLiveStream:
    start_time: datetime = faker.future_datetime()
    return CreateLiveStream(
        title=faker.company(),
        start_time=start_time.isoformat(),
        end_time=(start_time + timedelta(hours=2)).isoformat(),
        image=faker.file_path(extension='jpg'),
        genres=[faker.name() for _ in range(2)],
        url=faker.uri(),
        djs=[faker.name() for _ in range(2)],
    )


@pytest.fixture
async def livestream(
        livestream_data: CreateLiveStream,
) -> None | typing.Mapping:
    return await livestream_crud.create(livestream_data)


@pytest.fixture
async def livestream_in_a_month(
        livestream_data: CreateLiveStream,
) -> None | typing.Mapping:
    start_time = datetime.now() + timedelta(days=32)
    livestream_data.start_time = start_time
    livestream_data.end_time = start_time + timedelta(hours=2)
    return await livestream_crud.create(livestream_data)


@pytest.fixture
def dj_data(faker: Faker) -> CreateDJ:
    return CreateDJ(
        name=faker.name(),
        real_name=faker.name(),
        aliases=[faker.name() for _ in range(3)],
        country=faker.country(),
        genres=[faker.name() for _ in range(2)],
        image=faker.file_path(extension='jpg'),
        birth_date=faker.date(),
        site=faker.url(),
    )


@pytest.fixture
async def dj(dj_data: CreateDJ) -> None | typing.Mapping:
    return await djs_crud.create(dj_data)


@pytest.fixture
def group_data(
        faker: Faker,
        dj: typing.Mapping,
        dj_data: CreateDJ,
) -> CreateDJ:
    dj_data.name = faker.name()
    dj_data.slug = faker.slug()
    dj_data.is_group = True
    dj_data.group_members = [dj['id']]
    return dj_data


@pytest.fixture
async def group(group_data: CreateDJ) -> typing.Mapping:
    return await djs_crud.create(group_data)


@pytest.fixture
async def api_token(admin: typing.Mapping, faker: Faker) -> str:
    token = helpers.generate_token()
    await tokens_crud.add_token(faker.name(), token, admin['id'])
    return token


@pytest.fixture
async def ms_video(videos: list[typing.Mapping]) -> MeilisearchVideo:
    video = Video(**videos[0])
    task = await meilisearch_video_repository.create(video)
    await wait_for_task(
        meilisearch_video_repository.client.http_client,
        task.uid
    )
    return await meilisearch_video_repository.get_by_id(video.id)
