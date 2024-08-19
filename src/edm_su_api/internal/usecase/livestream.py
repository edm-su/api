from datetime import date, datetime, timedelta, timezone

from typing_extensions import Self

from edm_su_api.internal.entity.livestreams import (
    CreateLiveStreamDTO,
    LiveStream,
)
from edm_su_api.internal.usecase.exceptions.livestream import (
    LiveStreamAlreadyExistsError,
    LiveStreamNotFoundError,
)
from edm_su_api.internal.usecase.repository.livestream import (
    AbstractLiveStreamRepository,
)


class AbstractLiveStreamUseCase:
    def __init__(
        self: Self,
        repository: AbstractLiveStreamRepository,
    ) -> None:
        self.repository = repository


class GetAllLiveStreamsUseCase(AbstractLiveStreamUseCase):
    async def execute(
        self: Self,
        start: date | None = None,
        end: date | None = None,
    ) -> list[LiveStream]:
        if start is None:
            start = datetime.now(tz=timezone.utc).date() - timedelta(days=2)

        if end is None:
            end = datetime.now(tz=timezone.utc).date() + timedelta(days=31)

        return await self.repository.get_all(
            start=start,
            end=end,
        )


class GetLiveStreamUseCase(AbstractLiveStreamUseCase):
    async def execute(
        self: Self,
        live_stream_id: int,
    ) -> LiveStream:
        livestream = await self.repository.get_by_id(live_stream_id)
        if not livestream:
            raise LiveStreamNotFoundError
        return livestream


class CreateLiveStreamUseCase(AbstractLiveStreamUseCase):
    async def execute(
        self: Self,
        live_stream: CreateLiveStreamDTO,
    ) -> LiveStream:
        db_live_stream = await self.repository.get_by_slug(
            slug=live_stream.slug,
            start=live_stream.start_time,
            end=live_stream.end_time,
        )
        if db_live_stream:
            raise LiveStreamAlreadyExistsError(live_stream=live_stream)
        return await self.repository.create(live_stream=live_stream)


class UpdateLiveStreamUseCase(AbstractLiveStreamUseCase):
    async def execute(
        self: Self,
        live_stream: LiveStream,
    ) -> LiveStream:
        await self.repository.update(live_stream=live_stream)
        return live_stream


class DeleteLiveStreamUseCase(AbstractLiveStreamUseCase):
    async def execute(
        self: Self,
        live_stream_id: int,
    ) -> None:
        await self.repository.delete(live_stream_id=live_stream_id)
