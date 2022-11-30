class UserException(Exception):
    pass


class UserNotFoundException(UserException):
    def __init__(self, key: str, value: int | str) -> None:
        self.key = key
        self.value = value
        super().__init__(f"User with {key} {value} not found")


class UserAlreadyExistsException(UserException):
    def __init__(self, key: str, value: int | str | None = None) -> None:
        self.key = key
        self.value = value
        if value is None:
            super().__init__(f"User with {key} already exists")
        super().__init__(f"User with {key} {value} already exists")


class WrongActivationCodeException(UserException):
    def __init__(self) -> None:
        super().__init__(f"Wrong activation code")
