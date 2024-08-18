from typing_extensions import Self


class UserVideoError(Exception):
    pass


class UserVideoAlreadyLikedError(UserVideoError):
    def __init__(self: Self) -> None:
        super().__init__("User video already liked")


class UserVideoNotLikedError(UserVideoError):
    def __init__(self: Self) -> None:
        super().__init__("User video not liked")
