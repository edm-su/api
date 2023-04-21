from typing_extensions import Self


class UserTokensError(Exception):
    def __init__(
        self: Self,
        message: str,
    ) -> None:
        super().__init__(message)


class UserTokenNotFoundError(UserTokensError):
    def __init__(self: Self) -> None:
        super().__init__("Token not found or does not belong to this user")
