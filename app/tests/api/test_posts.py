from datetime import datetime, timedelta

import pytz
from starlette import status

from app.schemas.post import CreatePost, Post
from app.tests.helpers import create_auth_header


def test_read_posts(client, posts):
    response = client.get('/posts')

    assert response.status_code == status.HTTP_200_OK
    assert int(response.headers['x-total-count']) == len(posts)
    for post in response.json():
        assert Post.validate(post)


def test_read_post(client, posts):
    response = client.get(f'/posts/{posts[0]["slug"]}')

    assert response.status_code == status.HTTP_200_OK
    assert Post.validate(response.json())


def test_delete_post(client, posts, admin):
    response = client.delete(f'/posts/{posts[0]["slug"]}', headers=create_auth_header(admin['username']))

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_create_post(client, admin):
    published_at = datetime.utcnow().replace(tzinfo=pytz.UTC) + timedelta(minutes=1)
    new_post = CreatePost(title='Ещё одна заметка',
                          text='Ещё одна заметка',
                          slug='new-test-post',
                          published_at=published_at,
                          )
    response = client.post('/posts/',
                           data=new_post.json(exclude_unset=True),
                           headers=create_auth_header(admin['username']),
                           )

    assert response.status_code == status.HTTP_200_OK
    assert Post.validate(response.json())
