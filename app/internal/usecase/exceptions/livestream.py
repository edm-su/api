from app.internal.entity.livestreams import CreateLiveStream


class LiveStreamException(Exception):
    pass


class LiveStreamNotFoundException(LiveStreamException):
    def __init__(self, live_stream_id: int) -> None:
        self.live_stream_id = live_stream_id
        super().__init__(f"LiveStream with id {live_stream_id} not found")


class LiveStreamAlreadyExistsException(LiveStreamException):
    def __init__(self, live_stream: CreateLiveStream) -> None:
        self.live_stream = live_stream
        super().__init__(
            f"LiveStream with slug {live_stream.slug} already exists",
        )
