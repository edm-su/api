from typing_extensions import Self


class UserError(Exception):
    pass


class UserNotFoundError(UserError):
    def __init__(self: Self) -> None:
        super().__init__("User not found")


class UserAlreadyExistsError(UserError):
    def __init__(
        self: Self,
        key: str,
        value: int | str | None = None,
    ) -> None:
        self.key = key
        self.value = value
        if value is None:
            super().__init__(f"User with {key} already exists")
        super().__init__(f"User with {key} {value} already exists")


class WrongActivationCodeError(UserError):
    def __init__(self: Self) -> None:
        super().__init__("Wrong activation code")


class WrongPasswordError(UserError):
    def __init__(self: Self) -> None:
        super().__init__("Wrong password")


class WrongPasswordOrEmailError(UserError):
    def __init__(self: Self) -> None:
        super().__init__("Wrong password or email")


class UserIsBannedError(UserError):
    def __init__(self: Self) -> None:
        super().__init__("User is banned")


class AuthError(UserError):
    def __init__(self: Self) -> None:
        super().__init__("Authentication code error")


class UserNotActivatedError(UserError):
    def __init__(self: Self) -> None:
        super().__init__("User not activated")


class WrongResetCodeError(UserError):
    def __init__(self: Self) -> None:
        super().__init__("Wrong reset code")


class NeedOldPasswordOrResetCodeError(UserError):
    def __init__(self: Self) -> None:
        super().__init__("Need old password or reset code")
