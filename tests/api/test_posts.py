from datetime import datetime, timedelta, timezone
from typing import Mapping

import pytest
from httpx import AsyncClient
from starlette import status

from app.schemas.post import CreatePost, Post
from tests.helpers import create_auth_header


@pytest.mark.asyncio
async def test_read_posts(client: AsyncClient, posts: list[Mapping]) -> None:
    """
    Получение списка постов
    :param client:
    :param posts:
    :return:
    """
    response = await client.get('/posts')

    assert response.status_code == status.HTTP_200_OK
    assert int(response.headers['x-total-count']) == len(posts)
    for post in response.json():
        assert Post.validate(post)


@pytest.mark.asyncio
async def test_read_post(client: AsyncClient, posts: list[Mapping]) -> None:
    """
    Получение поста
    :param client:
    :param posts:
    :return:
    """
    response = await client.get(f'/posts/{posts[0]["slug"]}')

    assert response.status_code == status.HTTP_200_OK
    assert Post.validate(response.json())


@pytest.mark.asyncio
async def test_delete_post(
        client: AsyncClient,
        posts: list[Mapping],
        admin: dict,
) -> None:
    """
    Удаление поста
    :param client:
    :param posts:
    :param admin:
    :return:
    """
    response = await client.delete(
        f'/posts/{posts[0]["slug"]}',
        headers=create_auth_header(admin['username']),
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_create_post(client: AsyncClient, admin: Mapping) -> None:
    """
    Создание поста
    :param client:
    :param admin:
    :return:
    """
    published_at = datetime.now(timezone.utc) + timedelta(minutes=1)
    new_post = CreatePost(
        title='Ещё одна заметка',
        text={
            "time": 1605425931108,
            "blocks": [{"type": "paragraph", "data": {"text": "test"}}],
            "version": "2.19.0",
        },
        slug='new-test-post',
        published_at=published_at,
    )
    response = await client.post(
        '/posts',
        content=new_post.json(),
        headers=create_auth_header(admin['username']),
    )

    assert response.status_code == status.HTTP_200_OK
    assert Post.validate(response.json())
