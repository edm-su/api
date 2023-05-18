from typing_extensions import Self


class UserTokensError(Exception):
    pass


class UserTokenNotFoundError(UserTokensError):
    def __init__(self: Self) -> None:
        super().__init__("Token not found or does not belong to this user")
