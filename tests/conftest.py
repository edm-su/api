from asyncio import AbstractEventLoop, get_event_loop
from datetime import date, datetime
from typing import AsyncGenerator, Generator, List, Optional, Mapping, Dict, \
    Any

import pytest
from _pytest.monkeypatch import MonkeyPatch
from httpx import AsyncClient

from app import tasks
from app.crud.channel import create_channel
from app.crud.post import create_post
from app.crud.user import create_user, generate_recovery_user_code
from app.crud.video import add_video, like_video
from app.db import database
from app.main import app
from app.schemas.channel import BaseChannel
from app.schemas.post import BasePost


@pytest.fixture(scope='session')
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test') as client:
        yield client


@pytest.fixture(autouse=True)
async def db_connect() -> AsyncGenerator[None, None]:
    await database.connect()
    yield
    await database.disconnect()


@pytest.fixture(scope='session')
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    loop = get_event_loop()
    yield loop


@pytest.fixture()
async def videos() -> List[Optional[Mapping]]:
    videos_list: List[Dict[str, Any[str, int]]] = [
        {
            "title": "No Lockdown! - The Swedish Response",
            "slug": "no-lockdown-the-swedish-response-to",
            "date": "2020-05-13",
            "yt_id": "S_RE1qMTNZo",
            "yt_thumbnail": "https://i.ytimg.com/vi/S_RE1qMTNZo/default.jpg",
            "duration": 1936,
        },
        {
            "title": "Go Urmet Sessions #StaySafeEdition - 13.5.2020",
            "slug": "go-urmet-sessions-staysafeedition-13-5-2020",
            "date": "2020-05-13",
            "yt_id": "t69TGiADYMI",
            "yt_thumbnail": "https://i.ytimg.com/vi/t69TGiADYMI/default.jpg",
            "duration": 3516,
        },
        {
            "title": "Discoteque Credits #StaySafeEdition - 13.5.2020",
            "slug": "discoteque-credits-staysafeedition-13-5-2020",
            "date": "2020-05-13",
            "yt_id": "oPSsSFrMdbY",
            "yt_thumbnail": "https://i.ytimg.com/vi/oPSsSFrMdbY/default.jpg",
            "duration": 3452,
        }
    ]
    result = []
    for video in videos_list:
        result.append(
            await add_video(
                video['title'],
                video['slug'],
                video['yt_id'],
                video['yt_thumbnail'],
                date.fromisoformat(video['date']),
                duration=video['duration']
            ),
        )
    return result


@pytest.fixture()
async def posts(admin: Mapping) -> List[Optional[Mapping]]:
    posts_list = [
        BasePost(
            title='Новая заметка',
            text='Это заметка для тестов',
            slug='test',
            published_at=datetime.now(),
        )
    ]
    result = []
    for post in posts_list:
        new_post = await create_post(post, admin['id'])
        result.append(new_post)
    return result


@pytest.fixture()
async def liked_video(
        admin: Mapping,
        videos: List[Mapping],
) -> Mapping:
    await like_video(admin['id'], videos[0]['id'])
    return videos[0]


@pytest.fixture()
async def admin() -> Optional[Mapping]:
    return await create_user(
        username='Admin',
        email='admin@example.com',
        password='password',
        is_admin=True,
    )


@pytest.fixture()
async def non_activated_user() -> Optional[Mapping]:
    return await create_user(
        'Usernonactiv',
        'usernonactiv@example.com',
        'password'
    )


@pytest.fixture()
async def user() -> Optional[Mapping]:
    return await create_user(
        'User',
        'user@example.com',
        'password',
        is_active=True,
    )


@pytest.fixture()
async def channel_to_be_deleted() -> Optional[Mapping]:
    channel = BaseChannel(
        name='Channel to be deleted',
        slug='channel_to_be_deleted',
        yt_id='test',
        yt_thumbnail='test'
    )
    return await create_channel(channel)


@pytest.fixture()
async def recovered_user_code(admin: dict) -> str:
    return await generate_recovery_user_code(admin['id'])


@pytest.fixture(autouse=True)
def no_send_email(monkeypatch: MonkeyPatch) -> None:
    def mock_send_email(*args: list, **kwargs: dict) -> None:
        pass

    monkeypatch.setattr(tasks, 'send_email', mock_send_email)
