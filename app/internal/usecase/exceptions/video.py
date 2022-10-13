class VideoException(Exception):
    message = "Video error"


class SlugNotUniqueException(VideoException):
    def __init__(self, slug: str, entity: str) -> None:
        self.message = f"{entity.upper()} with slug {slug} already exists"


class VideoYtIdNotUniqueException(VideoException):
    def __init__(self, yt_id: str) -> None:
        self.message = f"Video with yt_id {yt_id} already exists"


class NotFoundException(VideoException):
    def __init__(self, entity: str) -> None:
        self.message = f"{entity.upper()} not found"


class NotDeletedException(VideoException):
    def __init__(self, entity: str) -> None:
        self.message = f"{entity.upper()} not deleted"
