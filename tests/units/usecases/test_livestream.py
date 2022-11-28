from datetime import timezone
from unittest.mock import AsyncMock

import pytest
from faker import Faker
from pytest_mock import MockerFixture

from app.internal.entity.livestreams import CreateLiveStream
from app.internal.usecase.exceptions.livestream import (
    LiveStreamAlreadyExistsException,
    LiveStreamNotFoundException,
)
from app.internal.usecase.livestream import (
    CreateLiveStreamUseCase,
    DeleteLiveStreamUseCase,
    GetAllLiveStreamsUseCase,
    GetLiveStreamUseCase,
    UpdateLiveStreamUseCase,
)
from app.internal.usecase.repository.livestream import (
    PostgresLiveStreamRepository,
)
from app.schemas.livestreams import LiveStream


@pytest.fixture
def repository(mocker: MockerFixture) -> PostgresLiveStreamRepository:
    session = mocker.MagicMock()
    return PostgresLiveStreamRepository(session)


@pytest.fixture
def livestream(faker: Faker) -> LiveStream:
    return LiveStream(
        id=faker.pyint(),
        title=faker.pystr(),
        slug=faker.slug(),
        cancelled=faker.pybool(),
        djs=faker.pylist(value_types=(str,)),
        end_time=faker.future_datetime(tzinfo=timezone.utc),
        start_time=faker.future_datetime(tzinfo=timezone.utc),
        genres=faker.pylist(value_types=(str,)),
        image=faker.url(),
        url=faker.url(),
    )


@pytest.fixture
def new_livestream(faker: Faker, livestream: LiveStream) -> CreateLiveStream:
    return CreateLiveStream(
        title=livestream.title,
        slug=livestream.slug,
        cancelled=livestream.cancelled,
        djs=livestream.djs,
        end_time=livestream.end_time,
        start_time=livestream.start_time,
        genres=livestream.genres,
        image=livestream.image,
        url=livestream.url,
    )


class TestCreateLiveStreamUseCase:
    @pytest.fixture(autouse=True)
    def mock(
        self,
        mocker: MockerFixture,
        faker: Faker,
        livestream: LiveStream,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.livestream."
            "PostgresLiveStreamRepository."
            "create",
            return_value=livestream,
        )
        mocker.patch(
            "app.internal.usecase.repository.livestream."
            "PostgresLiveStreamRepository."
            "get_by_slug",
            return_value=None,
        )

    @pytest.fixture
    def usecase(
        self,
        repository: PostgresLiveStreamRepository,
    ) -> CreateLiveStreamUseCase:
        return CreateLiveStreamUseCase(repository)

    async def test_create_livestream(
        self,
        usecase: AsyncMock,
        livestream: LiveStream,
        new_livestream: CreateLiveStream,
    ) -> None:
        assert await usecase.execute(new_livestream) == livestream

        usecase.repository.create.assert_awaited_once()

    async def test_create_already_existing_livestream(
        self,
        usecase: AsyncMock,
        livestream: LiveStream,
        new_livestream: CreateLiveStream,
        mocker: MockerFixture,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.livestream."
            "PostgresLiveStreamRepository."
            "get_by_slug",
            return_value=livestream,
        )

        with pytest.raises(LiveStreamAlreadyExistsException):
            await usecase.execute(new_livestream)

        usecase.repository.create.assert_not_awaited()


class TestGetAllLiveStreamsUseCase:
    @pytest.fixture(autouse=True)
    def mock(
        self,
        mocker: MockerFixture,
        faker: Faker,
        livestream: LiveStream,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.livestream."
            "PostgresLiveStreamRepository."
            "get_all",
            return_value=[livestream],
        )

    @pytest.fixture
    def usecase(
        self,
        repository: PostgresLiveStreamRepository,
    ) -> GetAllLiveStreamsUseCase:
        return GetAllLiveStreamsUseCase(repository)

    async def test_get_all_livestreams(
        self,
        usecase: AsyncMock,
        livestream: LiveStream,
    ) -> None:
        assert await usecase.execute() == [livestream]

        usecase.repository.get_all.assert_awaited_once()


class TestGetLiveStreamUseCase:
    @pytest.fixture(autouse=True)
    def mock(
        self,
        mocker: MockerFixture,
        faker: Faker,
        livestream: LiveStream,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.livestream."
            "PostgresLiveStreamRepository."
            "get_by_id",
            return_value=livestream,
        )

    @pytest.fixture
    def usecase(
        self,
        repository: PostgresLiveStreamRepository,
    ) -> GetLiveStreamUseCase:
        return GetLiveStreamUseCase(repository)

    async def test_get_livestream(
        self,
        usecase: AsyncMock,
        livestream: LiveStream,
    ) -> None:
        assert await usecase.execute(livestream.id) == livestream

        usecase.repository.get_by_id.assert_awaited_once()


class TestUpdateLiveStreamUseCase:
    @pytest.fixture(autouse=True)
    def mock(
        self,
        mocker: MockerFixture,
        faker: Faker,
        livestream: LiveStream,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.livestream."
            "PostgresLiveStreamRepository."
            "update",
            return_value=livestream,
        )
        mocker.patch(
            "app.internal.usecase.repository.livestream."
            "PostgresLiveStreamRepository."
            "get_by_slug",
            return_value=None,
        )

    @pytest.fixture
    def usecase(
        self,
        repository: PostgresLiveStreamRepository,
    ) -> UpdateLiveStreamUseCase:
        return UpdateLiveStreamUseCase(repository)

    async def test_update_livestream(
        self,
        usecase: AsyncMock,
        livestream: LiveStream,
    ) -> None:
        livestream.title = "new title"
        assert await usecase.execute(livestream) == livestream

        usecase.repository.update.assert_awaited_once()

    async def test_update_not_existing_livestream(
        self,
        usecase: AsyncMock,
        livestream: LiveStream,
        mocker: MockerFixture,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.livestream."
            "PostgresLiveStreamRepository."
            "update",
            return_value=False,
        )
        with pytest.raises(LiveStreamNotFoundException):
            await usecase.execute(livestream)

        usecase.repository.update.assert_awaited_once()


class TestDeleteLiveStreamUseCase:
    @pytest.fixture(autouse=True)
    def mock(
        self,
        mocker: MockerFixture,
        faker: Faker,
        livestream: LiveStream,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.livestream."
            "PostgresLiveStreamRepository."
            "delete",
            return_value=True,
        )

    @pytest.fixture
    def usecase(
        self,
        repository: PostgresLiveStreamRepository,
    ) -> DeleteLiveStreamUseCase:
        return DeleteLiveStreamUseCase(repository)

    async def test_delete_livestream(
        self,
        usecase: AsyncMock,
        livestream: LiveStream,
    ) -> None:
        assert await usecase.execute(livestream.id) is None

        usecase.repository.delete.assert_awaited_once()

    async def test_delete_not_existing_livestream(
        self,
        usecase: AsyncMock,
        mocker: MockerFixture,
    ) -> None:
        mocker.patch(
            "app.internal.usecase.repository.livestream."
            "PostgresLiveStreamRepository."
            "delete",
            return_value=None,
        )

        with pytest.raises(LiveStreamNotFoundException):
            await usecase.execute(0)

        usecase.repository.delete.assert_awaited_once()
