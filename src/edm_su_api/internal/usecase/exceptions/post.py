from typing_extensions import Self


class PostError(Exception):
    pass


class PostWasNotDeletedError(PostError):
    def __init__(self: Self) -> None:
        super().__init__("post was not deleted")


class PostNotFoundError(PostError):
    def __init__(self: Self) -> None:
        super().__init__("post not found")


class PostSlugNotUniqueError(PostError):
    def __init__(self: Self, slug: str) -> None:
        super().__init__(f"post with slug {slug} already exists")
