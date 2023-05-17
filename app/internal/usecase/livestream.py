from datetime import date, timedelta

from typing_extensions import Self

from app.internal.entity.livestreams import CreateLiveStream, LiveStream
from app.internal.usecase.exceptions.livestream import (
    LiveStreamAlreadyExistsError,
    LiveStreamError,
    LiveStreamNotFoundError,
)
from app.internal.usecase.repository.livestream import (
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
        start: date = date.today() - timedelta(days=2),
        end: date = date.today() + timedelta(days=31),
    ) -> list[LiveStream | None]:
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
            raise LiveStreamNotFoundError(live_stream_id)
        return livestream


class CreateLiveStreamUseCase(AbstractLiveStreamUseCase):
    async def execute(
        self: Self,
        live_stream: CreateLiveStream,
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
        updated = await self.repository.update(live_stream=live_stream)
        if not updated:
            raise LiveStreamError
        return live_stream


class DeleteLiveStreamUseCase(AbstractLiveStreamUseCase):
    async def execute(
        self: Self,
        live_stream_id: int,
    ) -> None:
        deleted = await self.repository.delete(live_stream_id=live_stream_id)
        if not deleted:
            raise LiveStreamError
