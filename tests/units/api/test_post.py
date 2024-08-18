from datetime import timezone

import pytest
from faker import Faker
from fastapi import status
from httpx import AsyncClient
from pytest_mock import MockerFixture
from typing_extensions import Self

from app.internal.controller.http import app
from app.internal.controller.http.v1.dependencies.post import find_post
from app.internal.controller.http.v1.requests.post import CreatePostRequest
from app.internal.entity.post import Post
from app.internal.entity.user import User
from app.internal.usecase.exceptions.post import (
    PostNotFoundError,
    PostSlugNotUniqueError,
    PostWasNotDeletedError,
)


@pytest.fixture
def new_post_data(
    faker: Faker,
) -> CreatePostRequest:
    return CreatePostRequest(
        title=faker.word(),
        slug=faker.slug(),
        text={
            "time": 1663421283682,
            "blocks": [
                {
                    "id": "OPKxUFrgdd",
                    "type": "paragraph",
                    "data": {
                        "text": faker.paragraph(),
                    },
                },
            ],
            "version": "2.24.3",
        },
        published_at=faker.future_datetime(tzinfo=timezone.utc),
    )


@pytest.fixture
def post(
    new_post_data: CreatePostRequest,
    user: User,
) -> Post:
    return Post(
        **new_post_data.model_dump(),
        id=1,
        user_id=user.id,
    )


class TestNewPost:
    @pytest.mark.usefixtures("mock_current_user")
    async def test_new_post(
        self: Self,
        client: AsyncClient,
        new_post_data: CreatePostRequest,
        post: Post,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.post.CreatePostUseCase.execute",
            return_value=post,
        )
        data = new_post_data.model_dump()
        data["published_at"] = (
            data["published_at"]
            .replace(
                tzinfo=timezone.utc,
            )
            .isoformat()
        )
        response = await client.post(
            "/posts",
            json=data,
        )
        response_data = response.json()

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_201_CREATED
        assert response_data["id"] == post.id

    @pytest.mark.usefixtures("mock_current_user")
    async def test_already_exists_post(
        self: Self,
        client: AsyncClient,
        new_post_data: CreatePostRequest,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.post.CreatePostUseCase.execute",
            side_effect=PostSlugNotUniqueError(new_post_data.slug),
        )
        response = await client.post(
            "/posts",
            content=new_post_data.model_dump_json(exclude={"published_at"}),
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_409_CONFLICT


class TestGetAllPosts:
    async def test_get_posts(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
        post: Post,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.post.GetAllPostsUseCase.execute",
            return_value=[post],
        )
        mocked_count = mocker.patch(
            "app.internal.usecase.post.GetPostCountUseCase.execute",
            return_value=1,
        )
        response = await client.get("/posts")
        response_data = response.json()

        mocked.assert_awaited_once()
        mocked_count.assert_awaited_once()
        assert response.status_code == status.HTTP_200_OK
        assert len(response_data) == 1
        assert response_data[0]["id"] == post.id
        assert response.headers["X-Total-Count"] == "1"


class TestGetPost:
    async def test_get_post(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
        post: Post,
    ) -> None:
        app.dependency_overrides[find_post] = lambda: post
        response = await client.get(f"/posts/{post.slug}")
        response_data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert response_data["id"] == post.id


class TestDeletePost:
    @pytest.mark.usefixtures("mock_current_user")
    async def test_delete_post(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
        post: Post,
    ) -> None:
        app.dependency_overrides[find_post] = lambda: post
        mocked = mocker.patch(
            "app.internal.usecase.post.DeletePostUseCase.execute",
        )
        response = await client.delete(f"/posts/{post.slug}")

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.usefixtures("mock_current_user")
    async def test_not_found(
        self: Self,
        client: AsyncClient,
        post: Post,
        mocker: MockerFixture,
    ) -> None:
        app.dependency_overrides[find_post] = lambda: post
        mocked = mocker.patch(
            "app.internal.usecase.post.DeletePostUseCase.execute",
            side_effect=PostNotFoundError,
        )
        response = await client.delete(f"/posts/{post.slug}")

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.usefixtures("mock_current_user")
    async def test_another_error(
        self: Self,
        client: AsyncClient,
        post: Post,
        mocker: MockerFixture,
    ) -> None:
        app.dependency_overrides[find_post] = lambda: post
        mocked = mocker.patch(
            "app.internal.usecase.post.DeletePostUseCase.execute",
            side_effect=PostWasNotDeletedError,
        )
        response = await client.delete(f"/posts/{post.slug}")

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
