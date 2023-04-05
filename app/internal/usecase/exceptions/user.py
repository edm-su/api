from typing_extensions import Self


class UserError(Exception):
    pass


class UserNotFoundError(UserError):
    def __init__(
        self: Self,
        key: str,
        value: int | str,
    ) -> None:
        self.key = key
        self.value = value
        super().__init__(f"User with {key} {value} not found")


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


class WrongResetCodeError(UserError):
    def __init__(self: Self) -> None:
        super().__init__("Wrong reset code")


class NeedOldPasswordOrResetCodeError(UserError):
    def __init__(self: Self) -> None:
        super().__init__("Need old password or reset code")
