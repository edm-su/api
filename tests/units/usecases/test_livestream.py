from datetime import timezone
from unittest.mock import AsyncMock

import pytest
from faker import Faker
from pytest_mock import MockerFixture
from typing_extensions import Self

from app.internal.entity.livestreams import CreateLiveStream, LiveStream
from app.internal.usecase.exceptions.livestream import (
    LiveStreamAlreadyExistsError,
    LiveStreamError,
    LiveStreamNotFoundError,
)
from app.internal.usecase.livestream import (
    CreateLiveStreamUseCase,
    DeleteLiveStreamUseCase,
    GetAllLiveStreamsUseCase,
    GetLiveStreamUseCase,
    UpdateLiveStreamUseCase,
)
from app.internal.usecase.repository.livestream import (
    AbstractLiveStreamRepository,
)


@pytest.fixture()
def repository(mocker: MockerFixture) -> AbstractLiveStreamRepository:
    return AsyncMock(repr=AbstractLiveStreamRepository)


@pytest.fixture()
def livestream(faker: Faker) -> LiveStream:
    return LiveStream(
        id=faker.pyint(),
        title=faker.pystr(),
        slug=faker.slug(),
        cancelled=faker.pybool(),
        end_time=faker.date_time_between(
            start_date="+1h",
            end_date="+3h",
            tzinfo=timezone.utc,
        ),
        start_time=faker.date_time_between(
            start_date="now",
            end_date="+1h",
            tzinfo=timezone.utc,
        ),
        genres=faker.pylist(value_types=(str,)),
        image=faker.url(),
        url=faker.url(),
    )


@pytest.fixture()
def new_livestream(faker: Faker, livestream: LiveStream) -> CreateLiveStream:
    return CreateLiveStream(
        title=livestream.title,
        slug=livestream.slug,
        cancelled=livestream.cancelled,
        end_time=livestream.end_time,
        start_time=livestream.start_time,
        genres=livestream.genres,
        image=livestream.image,
        url=livestream.url,
    )


class TestCreateLiveStreamUseCase:
    @pytest.fixture(autouse=True)
    def _mock(
        self: Self,
        repository: AsyncMock,
        livestream: LiveStream,
    ) -> None:
        repository.create.return_value = livestream
        repository.get_by_slug.return_value = None

    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> CreateLiveStreamUseCase:
        return CreateLiveStreamUseCase(repository)

    async def test_create_livestream(
        self: Self,
        usecase: CreateLiveStreamUseCase,
        livestream: LiveStream,
        new_livestream: CreateLiveStream,
        repository: AsyncMock,
    ) -> None:
        assert await usecase.execute(new_livestream) == livestream

        repository.create.assert_awaited_once()

    async def test_create_already_existing_livestream(
        self: Self,
        usecase: CreateLiveStreamUseCase,
        livestream: LiveStream,
        new_livestream: CreateLiveStream,
        repository: AsyncMock,
    ) -> None:
        repository.get_by_slug.return_value = livestream

        with pytest.raises(LiveStreamAlreadyExistsError):
            await usecase.execute(new_livestream)

        repository.create.assert_not_awaited()


class TestGetAllLiveStreamsUseCase:
    @pytest.fixture(autouse=True)
    def _mock(
        self: Self,
        livestream: LiveStream,
        repository: AsyncMock,
    ) -> None:
        repository.get_all.return_value = [livestream]

    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> GetAllLiveStreamsUseCase:
        return GetAllLiveStreamsUseCase(repository)

    async def test_get_all_livestreams(
        self: Self,
        usecase: GetAllLiveStreamsUseCase,
        livestream: LiveStream,
        repository: AsyncMock,
    ) -> None:
        assert await usecase.execute() == [livestream]

        repository.get_all.assert_awaited_once()


class TestGetLiveStreamUseCase:
    @pytest.fixture(autouse=True)
    def _mock(
        self: Self,
        livestream: LiveStream,
        repository: AsyncMock,
    ) -> None:
        repository.get_by_id.return_value = livestream

    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> GetLiveStreamUseCase:
        return GetLiveStreamUseCase(repository)

    async def test_get_livestream(
        self: Self,
        usecase: GetLiveStreamUseCase,
        livestream: LiveStream,
        repository: AsyncMock,
    ) -> None:
        assert await usecase.execute(livestream.id) == livestream

        repository.get_by_id.assert_awaited_once()

    async def test_livestream_not_found(
        self: Self,
        usecase: GetLiveStreamUseCase,
        repository: AsyncMock,
        livestream: LiveStream,
    ) -> None:
        repository.get_by_id.return_value = None

        with pytest.raises(LiveStreamNotFoundError):
            await usecase.execute(livestream.id)
        repository.get_by_id.assert_awaited_once()


class TestUpdateLiveStreamUseCase:
    @pytest.fixture(autouse=True)
    def _mock(
        self: Self,
        livestream: LiveStream,
        repository: AsyncMock,
    ) -> None:
        repository.get_by_slug.return_value = None
        repository.update.return_value = livestream

    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> UpdateLiveStreamUseCase:
        return UpdateLiveStreamUseCase(repository)

    async def test_update_livestream(
        self: Self,
        usecase: UpdateLiveStreamUseCase,
        livestream: LiveStream,
        repository: AsyncMock,
    ) -> None:
        livestream.title = "new title"
        assert await usecase.execute(livestream) == livestream

        repository.update.assert_awaited_once()

    async def test_update_not_existing_livestream(
        self: Self,
        usecase: UpdateLiveStreamUseCase,
        livestream: LiveStream,
        repository: AsyncMock,
    ) -> None:
        repository.update.return_value = False

        with pytest.raises(LiveStreamError):
            await usecase.execute(livestream)

        repository.update.assert_awaited_once()


class TestDeleteLiveStreamUseCase:
    @pytest.fixture(autouse=True)
    def _mock(
        self: Self,
        repository: AsyncMock,
    ) -> None:
        repository.delete.return_value = True

    @pytest.fixture()
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> DeleteLiveStreamUseCase:
        return DeleteLiveStreamUseCase(repository)

    async def test_delete_livestream(
        self: Self,
        usecase: DeleteLiveStreamUseCase,
        livestream: LiveStream,
        repository: AsyncMock,
    ) -> None:
        await usecase.execute(livestream.id)

        repository.delete.assert_awaited_once()

    async def test_delete_not_existing_livestream(
        self: Self,
        usecase: DeleteLiveStreamUseCase,
        repository: AsyncMock,
    ) -> None:
        repository.delete.return_value = None

        with pytest.raises(LiveStreamError):
            await usecase.execute(0)

        repository.delete.assert_awaited_once()
