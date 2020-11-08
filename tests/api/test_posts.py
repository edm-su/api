from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from starlette import status

from app.schemas.post import CreatePost, Post
from tests.helpers import create_auth_header


@pytest.mark.asyncio
async def test_read_posts(client: AsyncClient, posts: dict):
    response = await client.get('/posts')

    assert response.status_code == status.HTTP_200_OK
    assert int(response.headers['x-total-count']) == len(posts)
    for post in response.json():
        assert Post.validate(post)


@pytest.mark.asyncio
async def test_read_post(client: AsyncClient, posts: dict):
    response = await client.get(f'/posts/{posts[0]["slug"]}')

    assert response.status_code == status.HTTP_200_OK
    assert Post.validate(response.json())


@pytest.mark.asyncio
async def test_delete_post(client: AsyncClient, posts: dict, admin: dict):
    response = await client.delete(
        f'/posts/{posts[0]["slug"]}',
        headers=create_auth_header(admin['username']),
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_create_post(client: AsyncClient, admin: dict):
    published_at = datetime.now(timezone.utc) + timedelta(minutes=1)
    new_post = CreatePost(
        title='Ещё одна заметка',
        text='Ещё одна заметка',
        slug='new-test-post',
        published_at=published_at,
    )
    response = await client.post(
        '/posts/',
        data=new_post.json(),
        headers=create_auth_header(admin['username']),
    )

    assert response.status_code == status.HTTP_200_OK
    assert Post.validate(response.json())