from typing_extensions import Self

from app.internal.entity.user import User, UserToken, UserTokenDTO
from app.internal.usecase.exceptions.user_tokens import UserTokenNotFoundError
from app.internal.usecase.repository.user_tokens import (
    AbstractUserTokensRepository,
)


class BaseUserTokensUseCase():
    def __init__(
        self: Self,
        repository: AbstractUserTokensRepository,
    ) -> None:
        self.repository = repository

class GetAllUserTokensUseCase(BaseUserTokensUseCase):
    async def execute(
        self: Self,
        user: User,
    ) -> list[UserToken | None]:
        return await self.repository.get_user_tokens(user)

class RevokeUserTokenUseCase(BaseUserTokensUseCase):
    async def execute(
        self: Self,
        token_id: int,
        user: User,
    ) -> None:
        token = await self.repository.get_by_id(token_id, user)
        if not token:
            raise UserTokenNotFoundError
        await self.repository.revoke(token, user)

class CreateUserTokenUseCase(BaseUserTokensUseCase):
    async def execute(
        self: Self,
        token: UserTokenDTO,
        user: User,
    ) -> UserToken:
        return await self.repository.create(token, user)
