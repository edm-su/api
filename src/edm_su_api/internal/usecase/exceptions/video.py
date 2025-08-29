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


class VideoAlreadyDeletedError(VideoError):
    def __init__(
        self: Self,
    ) -> None:
        super().__init__("Video is already deleted")


class VideoNotDeletedError(VideoError):
    def __init__(
        self: Self,
    ) -> None:
        super().__init__("Video is not deleted")


class VideoRestoreError(VideoError):
    def __init__(
        self: Self,
        message: str = "Failed to restore video",
    ) -> None:
        super().__init__(message)
