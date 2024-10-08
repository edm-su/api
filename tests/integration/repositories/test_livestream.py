import pytest
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Self

from edm_su_api.internal.entity.livestreams import (
    CreateLiveStreamDTO,
    LiveStream,
)
from edm_su_api.internal.usecase.exceptions.livestream import (
    LiveStreamNotFoundError,
)
from edm_su_api.internal.usecase.repository.livestream import (
    PostgresLiveStreamRepository,
)

pytestmark = pytest.mark.anyio


class TestPostgresLiveStreamRepository:
    @pytest.fixture
    def repository(
        self: Self,
        pg_session: AsyncSession,
    ) -> PostgresLiveStreamRepository:
        return PostgresLiveStreamRepository(pg_session)

    @pytest.fixture
    def livestream_data(
        self: Self,
        faker: Faker,
    ) -> CreateLiveStreamDTO:
        return CreateLiveStreamDTO(
            title=faker.word(),
            slug=faker.word(),
            start_time=faker.date_time_between(
                start_date="+2h",
                end_date="+4h",
            ),
            end_time=faker.date_time_between(
                start_date="+4h",
                end_date="+6h",
            ),
            image=faker.url(),
            genres=[faker.word()],
            url=faker.url(),
        )

    @pytest.fixture
    async def livestream(
        self: Self,
        repository: PostgresLiveStreamRepository,
        livestream_data: CreateLiveStreamDTO,
    ) -> LiveStream:
        return await repository.create(livestream_data)

    async def test_get_by_id(
        self: Self,
        repository: PostgresLiveStreamRepository,
        livestream: LiveStream,
    ) -> None:
        result = await repository.get_by_id(livestream.id)

        assert result is not None
        assert result.id == livestream.id

        with pytest.raises(LiveStreamNotFoundError):
            await repository.get_by_id(999_999)

    async def test_get_by_slug(
        self: Self,
        repository: PostgresLiveStreamRepository,
        livestream: LiveStream,
    ) -> None:
        result = await repository.get_by_slug(livestream.slug)

        assert result is not None
        assert result.id == livestream.id

        with pytest.raises(LiveStreamNotFoundError):
            await repository.get_by_slug("wrong_slug")

    async def test_get_all(
        self: Self,
        repository: PostgresLiveStreamRepository,
        livestream: LiveStream,
    ) -> None:
        results = await repository.get_all()

        assert len(results) > 0
        assert livestream.id in [r.id for r in results if r is not None]

    async def test_create(
        self: Self,
        repository: PostgresLiveStreamRepository,
        livestream_data: CreateLiveStreamDTO,
    ) -> None:
        result = await repository.create(livestream_data)

        assert result.slug == livestream_data.slug

    async def test_update(
        self: Self,
        repository: PostgresLiveStreamRepository,
        livestream: LiveStream,
    ) -> None:
        livestream.title = "new title"
        await repository.update(livestream)

        db_livestream = await repository.get_by_id(livestream.id)

        assert db_livestream
        assert db_livestream.title == "new title"

        livestream.id = 999_999
        with pytest.raises(LiveStreamNotFoundError):
            await repository.update(livestream)

    async def test_delete(
        self: Self,
        repository: PostgresLiveStreamRepository,
        livestream: LiveStream,
    ) -> None:
        await repository.delete(livestream.id)

        with pytest.raises(LiveStreamNotFoundError):
            await repository.get_by_id(livestream.id)

        with pytest.raises(LiveStreamNotFoundError):
            await repository.delete(999_999)
