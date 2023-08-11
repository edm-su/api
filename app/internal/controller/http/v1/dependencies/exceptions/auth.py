from typing_extensions import Self


class TokenError(Exception):
    pass


class TokenScopeError(TokenError):
    def __init__(self: Self, scope: str) -> None:
        self.scope = scope
        super().__init__(f"You cannot request {scope} scope")
