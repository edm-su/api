import pytest
from faker import Faker
from fastapi import HTTPException, status
from httpx import AsyncClient
from pytest_mock import MockerFixture
from typing_extensions import Self

from app.internal.controller.http.v1.dependencies.video import find_video
from app.internal.entity.comment import Comment
from app.internal.entity.user import User
from app.internal.entity.video import Video
from app.main import app


@pytest.fixture()
def _mock_find_video(video: Video) -> None:
    app.dependency_overrides[find_video] = lambda: video


@pytest.fixture()
def comment(
    faker: Faker,
    user: User,
    video: Video,
) -> Comment:
    return Comment(
        text=faker.text(),
        id=faker.random_int(min=1, max=1000),
        user_id=user.id,
        video_id=video.id,
        published_at=faker.date_time(),
    )


class TestNewComment:
    @pytest.mark.usefixtures("_mock_current_user", "_mock_find_video")
    async def test_new_comment(
        self: Self,
        client: AsyncClient,
        video: Video,
        user_auth_headers: dict[str, str],
        mocker: MockerFixture,
        comment: Comment,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.comment.CreateCommentUseCase.execute",
            return_value=comment,
        )
        response = await client.post(
            f"/videos/{video.slug}/comments",
            json={"text": comment.text},
            headers=user_auth_headers,
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.usefixtures("_mock_find_video")
    async def test_new_comment_by_guest(
        self: Self,
        client: AsyncClient,
        video: Video,
        comment: Comment,
    ) -> None:
        response = await client.post(
            f"/videos/{video.slug}/comments",
            json={"text": comment.text},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.usefixtures("_mock_current_user", "_mock_find_video")
    async def test_new_comment_with_invalid_data(
        self: Self,
        client: AsyncClient,
        video: Video,
        comment: Comment,
    ) -> None:
        response = await client.post(
            f"/videos/{video.slug}/comments",
            json={},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.usefixtures("_mock_current_user")
    async def test_new_comment_without_video(
        self: Self,
        client: AsyncClient,
        comment: Comment,
        video: Video,
    ) -> None:
        def mock_find_video() -> Video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
            )

        app.dependency_overrides[find_video] = mock_find_video
        response = await client.post(
            f"/videos/{video.slug}/comments",
            json={"text": comment.text},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestReadComments:
    @pytest.mark.usefixtures("_mock_find_video")
    async def test_read_comments(
        self: Self,
        client: AsyncClient,
        video: Video,
        comment: Comment,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.comment.GetVideoCommentsUseCase.execute",
            return_value=[comment],
        )
        response = await client.get(
            f"/videos/{video.slug}/comments",
        )
        response_data = response.json()

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_200_OK
        assert len(response_data) == 1
        assert response_data[0]["id"] == comment.id

    async def test_test_read_comments_without_video(
        self: Self,
        client: AsyncClient,
        video: Video,
    ) -> None:
        def mock_find_video() -> Video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
            )

        app.dependency_overrides[find_video] = mock_find_video
        response = await client.get(f"/videos/{video.slug}/comments")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetAllComments:
    @pytest.mark.usefixtures("_mock_current_admin")
    async def test_get_all_comments(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
        comment: Comment,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.comment.GetAllCommentsUseCase.execute",
            return_value=[comment],
        )
        mocker.patch(
            "app.internal.usecase.comment.GetCountCommentsUseCase.execute",
            return_value=1,
        )
        response = await client.get("/comments")
        response_data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert response_data[0]["id"] == comment.id
        assert response.headers["X-Total_Count"] == "1"
        mocked.assert_awaited_once()

    @pytest.mark.usefixtures("_mock_current_user")
    async def test_get_all_comments_by_not_admin(
        self: Self,
        client: AsyncClient,
    ) -> None:
        response = await client.get("/comments")
        assert response.status_code == status.HTTP_403_FORBIDDEN
