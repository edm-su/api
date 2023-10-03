from typing_extensions import Self


class VideoError(Exception):
    pass


class VideoYtIdNotUniqueError(VideoError):
    def __init__(
        self: Self,
        yt_id: str,
    ) -> None:
        super().__init__(f"Video with yt_id {yt_id} already exists")


class VideoNotFoundError(VideoError):
    def __init__(
        self: Self,
    ) -> None:
        super().__init__("Video not found")
