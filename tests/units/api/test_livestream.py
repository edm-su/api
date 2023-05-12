from datetime import timedelta

import pytest
from faker import Faker
from fastapi import status
from httpx import AsyncClient
from pytest_mock import MockerFixture
from typing_extensions import Self

from app.internal.controller.http.v1.dependencies.livestream import (
    find_live_stream,
)
from app.internal.entity.livestreams import CreateLiveStream, LiveStream
from app.internal.usecase.exceptions.livestream import (
    LiveStreamAlreadyExistsError,
    LiveStreamError,
)
from app.main import app


@pytest.fixture()
def new_stream_data(
    faker: Faker,
) -> CreateLiveStream:
    start_time = faker.date_time_this_month(
        before_now=False,
        after_now=True,
    )
    end_time = start_time + timedelta(hours=2)
    return CreateLiveStream(
        title=faker.word(),
        start_time=start_time,
        end_time=end_time,
        image=faker.image_url(),
        url=faker.url(),
        slug=faker.slug(),
        genres=faker.words(),
    )


@pytest.fixture()
def livestream(
    new_stream_data: CreateLiveStream,
) -> LiveStream:
    return LiveStream(**new_stream_data.dict(), id=1)


@pytest.fixture()
def _mock_find_livestream(livestream: LiveStream) -> None:
    app.dependency_overrides[find_live_stream] = lambda: livestream


class TestNewLiveStream:
    @pytest.mark.usefixtures("_mock_current_admin")
    async def test_new_live_stream(
        self: Self,
        client: AsyncClient,
        new_stream_data: CreateLiveStream,
        livestream: LiveStream,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.livestream.CreateLiveStreamUseCase.execute",
            return_value=livestream,
        )
        response = await client.post(
            "/livestreams/",
            content=new_stream_data.json(),
        )
        response_data = response.json()

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_201_CREATED
        assert response_data["id"] == livestream.id

    @pytest.mark.usefixtures("_mock_current_admin")
    async def test_already_exists_live_stream(
        self: Self,
        client: AsyncClient,
        new_stream_data: CreateLiveStream,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.livestream.CreateLiveStreamUseCase.execute",
            side_effect=LiveStreamAlreadyExistsError(
                live_stream=new_stream_data,
            ),
        )
        response = await client.post(
            "/livestreams/",
            content=new_stream_data.json(),
        )
        response_data = response.json()

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response_data["detail"] == "Live stream already exists"

    @pytest.mark.usefixtures("_mock_current_user")
    async def test_new_live_stream_without_permission(
        self: Self,
        client: AsyncClient,
        new_stream_data: CreateLiveStream,
    ) -> None:
        response = await client.post(
            "/livestreams/",
            content=new_stream_data.json(),
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetLiveStreams:
    async def test_get_live_streams(
        self: Self,
        client: AsyncClient,
        livestream: LiveStream,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.livestream.GetAllLiveStreamsUseCase.execute",
            return_value=[livestream],
        )
        response = await client.get("/livestreams/")
        response_data = response.json()

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_200_OK
        assert response_data[0]["id"] == livestream.id


class TestGetLiveStream:
    @pytest.mark.usefixtures("_mock_find_livestream")
    async def test_get_live_stream(
        self: Self,
        client: AsyncClient,
        livestream: LiveStream,
    ) -> None:
        response = await client.get(f"/livestreams/{livestream.id}")
        response_data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert response_data["id"] == livestream.id


class TestDeleteLiveStream:
    @pytest.mark.usefixtures("_mock_current_admin", "_mock_find_livestream")
    async def test_delete_live_stream(
        self: Self,
        client: AsyncClient,
        livestream: LiveStream,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.livestream.DeleteLiveStreamUseCase.execute",
        )
        response = await client.delete(f"/livestreams/{livestream.id}")

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.usefixtures("_mock_current_user", "_mock_find_livestream")
    async def test_delete_live_stream_without_permission(
        self: Self,
        client: AsyncClient,
        livestream: LiveStream,
    ) -> None:
        response = await client.delete(f"/livestreams/{livestream.id}")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.usefixtures("_mock_current_admin", "_mock_find_livestream")
    async def test_live_stream_was_not_deleted(
        self: Self,
        client: AsyncClient,
        livestream: LiveStream,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.livestream.DeleteLiveStreamUseCase.execute",
            side_effect=LiveStreamError(),
        )
        response = await client.delete(f"/livestreams/{livestream.id}")

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_409_CONFLICT


class TestUpdateLiveStream:
    @pytest.mark.usefixtures("_mock_current_admin", "_mock_find_livestream")
    async def test_update_live_stream(
        self: Self,
        client: AsyncClient,
        livestream: LiveStream,
        new_stream_data: CreateLiveStream,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.livestream.UpdateLiveStreamUseCase.execute",
            return_value=livestream,
        )
        response = await client.put(
            f"/livestreams/{livestream.id}",
            content=new_stream_data.json(),
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.usefixtures("_mock_current_user", "_mock_find_livestream")
    async def test_update_live_stream_without_permission(
        self: Self,
        client: AsyncClient,
        livestream: LiveStream,
        new_stream_data: CreateLiveStream,
    ) -> None:
        response = await client.put(
            f"/livestreams/{livestream.id}",
            content=new_stream_data.json(),
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.usefixtures("_mock_current_admin", "_mock_find_livestream")
    async def test_live_stream_was_not_updated(
        self: Self,
        client: AsyncClient,
        livestream: LiveStream,
        new_stream_data: CreateLiveStream,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.livestream.UpdateLiveStreamUseCase.execute",
            side_effect=LiveStreamError(),
        )
        response = await client.put(
            f"/livestreams/{livestream.id}",
            content=new_stream_data.json(),
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_409_CONFLICT
