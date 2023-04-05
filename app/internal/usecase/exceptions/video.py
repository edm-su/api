from typing_extensions import Self


class VideoError(Exception):
    message = "Video error"


class SlugNotUniqueError(VideoError):
    def __init__(
        self: Self,
        slug: str,
        entity: str,
    ) -> None:
        self.message = f"{entity.upper()} with slug {slug} already exists"


class VideoYtIdNotUniqueError(VideoError):
    def __init__(
        self: Self,
        yt_id: str,
    ) -> None:
        self.message = f"Video with yt_id {yt_id} already exists"


class NotFoundError(VideoError):
    def __init__(
        self: Self,
        entity: str,
    ) -> None:
        self.message = f"{entity.upper()} not found"


class NotDeletedError(VideoError):
    def __init__(
        self: Self,
        entity: str,
    ) -> None:
        self.message = f"{entity.upper()} not deleted"
