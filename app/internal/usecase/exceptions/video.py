class VideoException(Exception):
    message = "Video error"


class VideoSlugNotUniqueException(VideoException):
    def __init__(self, slug: str) -> None:
        self.message = f"Video with slug {slug} already exists"


class VideoYtIdNotUniqueException(VideoException):
    def __init__(self, yt_id: str) -> None:
        self.message = f"Video with yt_id {yt_id} already exists"


class VideoNotFoundException(VideoException):
    def __init__(self) -> None:
        self.message = f"Video not found"
