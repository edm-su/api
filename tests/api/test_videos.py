from collections.abc import Callable, Mapping
from typing import Any

import pytest
from httpx import AsyncClient
from meilisearch_python_async.errors import MeilisearchApiError
from slugify import slugify
from starlette import status
from tenacity import retry, stop_after_attempt, wait_fixed

from app.crud import video as videos_crud
from app.repositories.video import meilisearch_video_repository
from app.schemas.video import MeilisearchVideo, Video
from tests.helpers import create_auth_header


@retry(
    stop=stop_after_attempt(10),
    wait=wait_fixed(0.2),
)
async def async_retry(
    func: Callable,
    *args: Any,  # noqa: ANN401
    **kwargs: Any,  # noqa: ANN401
) -> Any:  # noqa: ANN401
    return await func(*args, **kwargs)


@pytest.mark.asyncio()
async def test_read_videos(client: AsyncClient, videos: Mapping) -> None:
    """
    Получение списка видео
    :param client:
    :param videos:
    :return:
    """
    response = await client.get("/videos")

    assert response.status_code == status.HTTP_200_OK
    for video in response.json():
        assert Video.validate(video)
    assert int(response.headers["x-total-count"]) == len(videos)


@pytest.mark.asyncio()
async def test_create_video(
    client: AsyncClient,
    admin: Mapping,
    video_data: Mapping,
) -> None:
    """
    Создание видео
    :param client:
    :param admin:
    :param video_data:
    :return:
    """
    auth_headers = create_auth_header(admin["username"])
    response = await client.post(
        "/videos",
        json=video_data,
        headers=auth_headers,
    )

    data = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    assert await videos_crud.get_video_by_slug(data["slug"])
    assert await async_retry(
        meilisearch_video_repository.get_by_id,
        data["id"],
    )


@pytest.mark.asyncio()
async def test_create_video_forbidden(
    client: AsyncClient,
    user: Mapping,
    video_data: Mapping,
) -> None:
    """
    Проверка прав на создание видео
    :param client:
    :param user:
    :param video_data:
    :return:
    """
    response = await client.post("/videos", json=video_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    slug = slugify(video_data["title"])
    assert not await videos_crud.get_video_by_slug(slug)

    auth_headers = create_auth_header(user["username"])
    response = await client.post(
        "/videos",
        json=video_data,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not await videos_crud.get_video_by_slug(slug)


@pytest.mark.asyncio()
async def test_video_already_exist(
    client: AsyncClient,
    admin: Mapping,
    videos: Mapping,
) -> None:
    """
    Проверка уникальности видео
    :param client:
    :param admin:
    :param videos:
    :return:
    """
    auth_headers = create_auth_header(admin["username"])
    video = dict(videos[0])
    video["date"] = video["date"].strftime("%Y-%m-%d")
    response = await client.post(
        "/videos",
        json=video,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    error = response.json()
    assert "Такой slug уже занят" in error["detail"]
    assert "Такой yt_id уже существует" in error["detail"]


@pytest.mark.asyncio()
async def test_delete_video(
    client: AsyncClient,
    videos: Mapping,
    ms_video: MeilisearchVideo,
    admin: Mapping,
) -> None:
    """
    Удаление видео
    :param client:
    :param videos:
    :param admin:
    :return:
    """
    headers = create_auth_header(admin["username"])
    response = await client.delete(
        f"/videos/{videos[0]['slug']}",
        headers=headers,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not await videos_crud.get_video_by_slug(videos[0]["slug"])
    with pytest.raises(MeilisearchApiError):
        await meilisearch_video_repository.get_by_id(ms_video.id)


@pytest.mark.asyncio()
async def test_delete_video_forbidden(
    client: AsyncClient,
    videos: Mapping,
    user: Mapping,
) -> None:
    """
    Проверка прав на удаление видео
    :param client:
    :param videos:
    :param user:
    :return:
    """
    video = videos[0]
    response = await client.delete(f"/videos/{video['slug']}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert await videos_crud.get_video_by_slug(video["slug"])

    auth_headers = create_auth_header(user["username"])
    response = await client.delete(
        f"/videos/{video['slug']}",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert await videos_crud.get_video_by_slug(video["slug"])


@pytest.mark.asyncio()
async def test_read_video(client: AsyncClient, videos: Mapping) -> None:
    """
    Получение видео
    :param client:
    :param videos:
    :return:
    """
    response = await client.get(f"/videos/{videos[0]['slug']}")

    assert response.status_code == status.HTTP_200_OK
    assert Video.validate(response.json())


@pytest.mark.asyncio()
async def test_read_related_videos(
    client: AsyncClient,
    videos: Mapping,
) -> None:
    """
    Полученеи списка похожих видео
    :param client:
    :param videos:
    :return:
    """
    response = await client.get(f"/videos/{videos[0]['slug']}/related")

    assert response.status_code == status.HTTP_200_OK
    for video in response.json():
        assert Video.validate(video)


@pytest.mark.asyncio()
async def test_like_video(
    client: AsyncClient,
    videos: Mapping,
    admin: Mapping,
) -> None:
    """
    Добавить видео в понравившиеся
    :param client:
    :param videos:
    :param admin:
    :return:
    """
    headers = create_auth_header(admin["username"])
    url = f"/videos/{videos[0]['slug']}/like"
    response = await client.post(url, headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio()
async def test_dislike_video(
    client: AsyncClient,
    liked_video: Mapping,
    admin: Mapping,
) -> None:
    """
    Удалить видео из понравившихся
    :param client:
    :param liked_video:
    :param admin:
    :return:
    """
    headers = create_auth_header(admin["username"])
    url = f"/videos/{liked_video['slug']}/like"
    response = await client.delete(url, headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio()
async def test_liked_videos(
    client: AsyncClient,
    liked_video: Mapping,
    admin: Mapping,
) -> None:
    """
    Получение списка понравивишхся видео
    :param client:
    :param liked_video:
    :param admin:
    :return:
    """
    headers = create_auth_header(admin["username"])
    response = await client.get("/users/liked_videos", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    for video in response.json():
        assert Video.validate(video)
    assert liked_video["slug"] in [video["slug"] for video in response.json()]


@pytest.mark.asyncio()
async def test_liked_videos_by_guest(
    client: AsyncClient,
    liked_video: Mapping,
) -> None:
    """
    Проверка авторизации для получения списка понравившихся видео
    :param client:
    :param liked_video:
    :return:
    """
    response = await client.get("/users/liked_videos")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
