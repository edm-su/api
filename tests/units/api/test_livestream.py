from datetime import timedelta

import pytest
from faker import Faker
from fastapi import status
from httpx import AsyncClient
from pytest_mock import MockerFixture
from typing_extensions import Self

from app.internal.controller.http import app
from app.internal.controller.http.v1.dependencies.livestream import (
    find_livestream,
)
from app.internal.entity.livestreams import CreateLiveStreamDTO, LiveStream
from app.internal.usecase.exceptions.livestream import (
    LiveStreamAlreadyExistsError,
    LiveStreamError,
)


@pytest.fixture
def new_stream_data(
    faker: Faker,
) -> CreateLiveStreamDTO:
    start_time = faker.date_time_this_month(
        before_now=False,
        after_now=True,
    )
    end_time = start_time + timedelta(hours=2)
    return CreateLiveStreamDTO(
        title=faker.word(),
        start_time=start_time,
        end_time=end_time,
        image=faker.image_url(),
        url=faker.url(),
        slug=faker.slug(),
        genres=faker.words(),
    )


@pytest.fixture
def livestream(
    new_stream_data: CreateLiveStreamDTO,
) -> LiveStream:
    return LiveStream(**new_stream_data.model_dump(), id=1)


@pytest.fixture
def mock_find_livestream(livestream: LiveStream) -> None:
    app.dependency_overrides[find_livestream] = lambda: livestream


class TestNewLiveStream:
    @pytest.mark.usefixtures("mock_current_user")
    async def test_new_live_stream(
        self: Self,
        client: AsyncClient,
        new_stream_data: CreateLiveStreamDTO,
        livestream: LiveStream,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.livestream.CreateLiveStreamUseCase.execute",
            return_value=livestream,
        )
        response = await client.post(
            "/livestreams",
            content=new_stream_data.model_dump_json(),
        )
        response_data = response.json()

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_201_CREATED
        assert response_data["id"] == livestream.id

    @pytest.mark.usefixtures("mock_current_user")
    async def test_already_exists_live_stream(
        self: Self,
        client: AsyncClient,
        new_stream_data: CreateLiveStreamDTO,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.livestream.CreateLiveStreamUseCase.execute",
            side_effect=LiveStreamAlreadyExistsError(
                live_stream=new_stream_data,
            ),
        )
        response = await client.post(
            "/livestreams",
            content=new_stream_data.model_dump_json(),
        )
        response_data = response.json()

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response_data["detail"] == "Live stream already exists"


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
        response = await client.get("/livestreams")
        response_data = response.json()

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_200_OK
        assert response_data[0]["id"] == livestream.id


class TestGetLiveStream:
    @pytest.mark.usefixtures("mock_find_livestream")
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
    @pytest.mark.usefixtures("mock_current_user", "mock_find_livestream")
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

    @pytest.mark.usefixtures("mock_current_user", "mock_find_livestream")
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
    @pytest.mark.usefixtures("mock_current_user", "mock_find_livestream")
    async def test_update_live_stream(
        self: Self,
        client: AsyncClient,
        livestream: LiveStream,
        new_stream_data: CreateLiveStreamDTO,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.livestream.UpdateLiveStreamUseCase.execute",
            return_value=livestream,
        )
        response = await client.put(
            f"/livestreams/{livestream.id}",
            content=new_stream_data.model_dump_json(),
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.usefixtures("mock_current_user", "mock_find_livestream")
    async def test_live_stream_was_not_updated(
        self: Self,
        client: AsyncClient,
        livestream: LiveStream,
        new_stream_data: CreateLiveStreamDTO,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.livestream.UpdateLiveStreamUseCase.execute",
            side_effect=LiveStreamError(),
        )
        response = await client.put(
            f"/livestreams/{livestream.id}",
            content=new_stream_data.model_dump_json(),
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_409_CONFLICT
