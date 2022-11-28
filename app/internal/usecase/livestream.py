from abc import ABC
from datetime import date, timedelta

from app.internal.entity.livestreams import CreateLiveStream
from app.internal.usecase.exceptions.livestream import (
    LiveStreamAlreadyExistsException,
    LiveStreamNotFoundException,
)
from app.internal.usecase.repository.livestream import (
    AbstractLiveStreamRepository,
)
from app.schemas.livestreams import LiveStream


class AbstractLiveStreamUseCase(ABC):
    def __init__(
        self,
        repository: AbstractLiveStreamRepository,
    ) -> None:
        self.repository = repository


class GetAllLiveStreamsUseCase(AbstractLiveStreamUseCase):
    async def execute(
        self,
        start: date = date.today() - timedelta(days=2),
        end: date = date.today() + timedelta(days=31),
    ) -> list[LiveStream | None]:
        return await self.repository.get_all(
            start=start,
            end=end,
        )


class GetLiveStreamUseCase(AbstractLiveStreamUseCase):
    async def execute(self, live_stream_id: int) -> LiveStream | None:
        return await self.repository.get_by_id(live_stream_id=live_stream_id)


class CreateLiveStreamUseCase(AbstractLiveStreamUseCase):
    async def execute(self, live_stream: CreateLiveStream) -> LiveStream:
        db_live_stream = await self.repository.get_by_slug(
            slug=live_stream.slug,
            start=live_stream.start_time,
            end=live_stream.end_time,
        )
        if db_live_stream:
            raise LiveStreamAlreadyExistsException(live_stream=live_stream)
        return await self.repository.create(live_stream=live_stream)


class UpdateLiveStreamUseCase(AbstractLiveStreamUseCase):
    async def execute(self, live_stream: LiveStream) -> LiveStream:
        updated = await self.repository.update(live_stream=live_stream)
        if not updated:
            raise LiveStreamNotFoundException(live_stream_id=live_stream.id)
        return live_stream


class DeleteLiveStreamUseCase(AbstractLiveStreamUseCase):
    async def execute(self, live_stream_id: int) -> None:
        deleted = await self.repository.delete(live_stream_id=live_stream_id)
        if not deleted:
            raise LiveStreamNotFoundException(live_stream_id=live_stream_id)
