import typing
from datetime import date, datetime

import pytest
from starlette.testclient import TestClient

from app.crud.post import create_post
from app.crud.user import create_user
from app.crud.video import add_video, like_video
from app.main import app
from app.schemas.post import BasePost


@pytest.fixture()
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture()
async def videos():
    videos_list = [
        {
            "title": "No Lockdown! - The Swedish Response to Coronavirus l ARTE Documentary",
            "slug": "no-lockdown-the-swedish-response-to-coronavirus-l-arte-documentary",
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
            await add_video(video['title'], video['slug'], video['yt_id'], video['yt_thumbnail'],
                            date.fromisoformat(video['date']), duration=video['duration']))
    return result


@pytest.fixture()
async def posts(admin):
    posts_list = [
        BasePost(title='Новая заметка', text='Это заметка для тестов', slug='test', published_at=datetime.now())
    ]
    result = []
    for post in posts_list:
        new_post = await create_post(post, admin['id'])
        result.append(new_post)
    return result


@pytest.fixture()
async def liked_video(admin: dict, videos: typing.List[dict]):
    await like_video(admin['id'], videos[0]['id'])
    return videos[0]


@pytest.fixture()
async def admin() -> typing.Mapping:
    return await create_user(username='Admin', email='admin@example.com', password='password', is_admin=True)
