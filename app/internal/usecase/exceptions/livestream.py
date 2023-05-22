from typing_extensions import Self

from app.internal.entity.livestreams import CreateLiveStreamDTO


class LiveStreamError(Exception):
    pass


class LiveStreamNotFoundError(LiveStreamError):
    def __init__(self: Self) -> None:
        super().__init__("LiveStream not found")


class LiveStreamAlreadyExistsError(LiveStreamError):
    def __init__(
        self: Self,
        live_stream: CreateLiveStreamDTO,
    ) -> None:
        super().__init__(
            f"LiveStream with slug {live_stream.slug} already exists",
        )
