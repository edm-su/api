from typing_extensions import Self


class PostError(Exception):
    pass


class PostNotDeletedError(PostError):
    def __init__(self: Self) -> None:
        super().__init__("post is not deleted")


class PostNotFoundError(PostError):
    def __init__(self: Self) -> None:
        super().__init__("post not found")
