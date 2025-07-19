from datetime import datetime, timezone

import pytest
from faker import Faker
from fastapi import status
from httpx import AsyncClient
from pytest_mock import MockerFixture
from typing_extensions import Self

from edm_su_api.internal.controller.http import app
from edm_su_api.internal.controller.http.v1.dependencies.post import find_post
from edm_su_api.internal.entity.post import (
    NewPost,
    Post,
    PostEditHistory,
    UpdatePost,
)
from edm_su_api.internal.entity.user import User
from edm_su_api.internal.usecase.exceptions.post import (
    PostNotFoundError,
    PostSlugNotUniqueError,
    PostWasNotDeletedError,
)

pytestmark = pytest.mark.anyio


@pytest.fixture
def new_post_data(
    faker: Faker,
) -> NewPost:
    return NewPost(
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
    new_post_data: NewPost,
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
        new_post_data: NewPost,
        post: Post,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "edm_su_api.internal.usecase.post.CreatePostUseCase.execute",
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
        new_post_data: NewPost,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "edm_su_api.internal.usecase.post.CreatePostUseCase.execute",
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
            "edm_su_api.internal.usecase.post.GetAllPostsUseCase.execute",
            return_value=[post],
        )
        mocked_count = mocker.patch(
            "edm_su_api.internal.usecase.post.GetPostCountUseCase.execute",
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
            "edm_su_api.internal.usecase.post.DeletePostUseCase.execute",
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
            "edm_su_api.internal.usecase.post.DeletePostUseCase.execute",
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
            "edm_su_api.internal.usecase.post.DeletePostUseCase.execute",
            side_effect=PostWasNotDeletedError,
        )
        response = await client.delete(f"/posts/{post.slug}")

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.fixture
def update_post_data(
    faker: Faker,
) -> UpdatePost:
    return UpdatePost(
        title=faker.sentence(),
        annotation=faker.paragraph(),
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
        thumbnail=faker.url(),
    )


@pytest.fixture
def post_edit_history(
    faker: Faker,
    post: Post,
    user: User,
) -> PostEditHistory:
    return PostEditHistory(
        id=faker.random_int(),
        post_id=post.id,
        edited_at=faker.past_datetime(tzinfo=timezone.utc),
        description=faker.sentence(),
        edited_by=user.id,
    )


class TestUpdatePost:
    @pytest.mark.usefixtures("mock_current_user")
    async def test_update_post_without_history(
        self: Self,
        client: AsyncClient,
        post: Post,
        update_post_data: UpdatePost,
        mocker: MockerFixture,
    ) -> None:
        app.dependency_overrides[find_post] = lambda: post
        post_dict = post.model_dump()
        post_dict.update(
            {
                "title": update_post_data.title,
                "updated_at": datetime.now(tz=timezone.utc),
                "updated_by": post.user_id,
            }
        )
        updated_post = Post(**post_dict)
        mocked = mocker.patch(
            "edm_su_api.internal.usecase.post.UpdatePostUseCase.execute",
            return_value=updated_post,
        )

        response = await client.put(
            f"/posts/{post.slug}",
            json=update_post_data.model_dump(exclude_unset=True),
        )
        response_data = response.json()

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_200_OK
        assert response_data["title"] == update_post_data.title

    @pytest.mark.usefixtures("mock_current_user")
    async def test_update_post_with_history(
        self: Self,
        client: AsyncClient,
        post: Post,
        update_post_data: UpdatePost,
        mocker: MockerFixture,
    ) -> None:
        app.dependency_overrides[find_post] = lambda: post
        post_dict = post.model_dump()
        post_dict.update(
            {
                "title": update_post_data.title,
                "updated_at": datetime.now(tz=timezone.utc),
                "updated_by": post.user_id,
            }
        )
        updated_post = Post(**post_dict)
        mocked = mocker.patch(
            "edm_su_api.internal.usecase.post.UpdatePostUseCase.execute",
            return_value=updated_post,
        )

        request_data = update_post_data.model_dump(exclude_unset=True)
        request_data["save_history"] = True
        request_data["history_description"] = "Title updated"

        response = await client.put(
            f"/posts/{post.slug}",
            json=request_data,
        )
        response_data = response.json()

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_200_OK
        assert response_data["title"] == update_post_data.title

    @pytest.mark.usefixtures("mock_current_user")
    async def test_update_post_with_history_no_description(
        self: Self,
        client: AsyncClient,
        post: Post,
        update_post_data: UpdatePost,
        mocker: MockerFixture,
    ) -> None:
        app.dependency_overrides[find_post] = lambda: post

        request_data = update_post_data.model_dump(exclude_unset=True)
        request_data["save_history"] = True

        response = await client.put(
            f"/posts/{post.slug}",
            json=request_data,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "history_description" in response.text

    @pytest.mark.usefixtures("mock_current_user")
    async def test_update_post_not_found(
        self: Self,
        client: AsyncClient,
        update_post_data: UpdatePost,
        mocker: MockerFixture,
    ) -> None:
        # For non-existent post find_post will throw 404
        response = await client.put(
            "/posts/non-existent-slug",
            json=update_post_data.model_dump(exclude_unset=True),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_post_unauthorized(
        self: Self,
        client: AsyncClient,
        post: Post,
        update_post_data: UpdatePost,
    ) -> None:
        response = await client.put(
            f"/posts/{post.slug}",
            json=update_post_data.model_dump(exclude_unset=True),
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetPostHistory:
    async def test_get_post_history(
        self: Self,
        client: AsyncClient,
        post: Post,
        post_edit_history: PostEditHistory,
        mocker: MockerFixture,
    ) -> None:
        app.dependency_overrides[find_post] = lambda: post
        mocked = mocker.patch(
            "edm_su_api.internal.usecase.post.GetPostHistoryUseCase.execute",
            return_value=[post_edit_history],
        )

        response = await client.get(f"/posts/{post.slug}/history")
        response_data = response.json()

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_200_OK
        assert len(response_data) == 1
        assert response_data[0]["id"] == post_edit_history.id
        assert response_data[0]["description"] == post_edit_history.description

    async def test_get_post_history_empty(
        self: Self,
        client: AsyncClient,
        post: Post,
        mocker: MockerFixture,
    ) -> None:
        app.dependency_overrides[find_post] = lambda: post
        mocked = mocker.patch(
            "edm_su_api.internal.usecase.post.GetPostHistoryUseCase.execute",
            return_value=[],
        )

        response = await client.get(f"/posts/{post.slug}/history")
        response_data = response.json()

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_200_OK
        assert len(response_data) == 0

    async def test_get_post_history_not_found(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
    ) -> None:
        response = await client.get("/posts/non-existent-slug/history")

        assert response.status_code == status.HTTP_404_NOT_FOUND
