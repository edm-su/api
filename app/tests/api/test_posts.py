from datetime import datetime, timedelta, timezone

from starlette import status
from starlette.testclient import TestClient

from app.schemas.post import CreatePost, Post
from app.tests.helpers import create_auth_header


def test_read_posts(client: TestClient, posts: dict):
    response = client.get('/posts')

    assert response.status_code == status.HTTP_200_OK
    assert int(response.headers['x-total-count']) == len(posts)
    for post in response.json():
        assert Post.validate(post)


def test_read_post(client: TestClient, posts: dict):
    response = client.get(f'/posts/{posts[0]["slug"]}')

    assert response.status_code == status.HTTP_200_OK
    assert Post.validate(response.json())


def test_delete_post(client: TestClient, posts: dict, admin: dict):
    response = client.delete(
        f'/posts/{posts[0]["slug"]}',
        headers=create_auth_header(admin['username']),
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_create_post(client: TestClient, admin: dict):
    published_at = datetime.now(timezone.utc) + timedelta(minutes=1)
    new_post = CreatePost(
        title='Ещё одна заметка',
        text='Ещё одна заметка',
        slug='new-test-post',
        published_at=published_at,
    )
    response = client.post(
        '/posts/',
        data=new_post.json(exclude_unset=True),
        headers=create_auth_header(admin['username']),
    )

    assert response.status_code == status.HTTP_200_OK
    assert Post.validate(response.json())
