from typing_extensions import Self

from edm_su_api.internal.usecase.repository.upload import (
    AbstractPreSignedUploadRepository,
)


class GeneratePreSignedUploadUseCase:
    def __init__(
        self: Self,
        repository: AbstractPreSignedUploadRepository,
    ) -> None:
        self.repository = repository

    async def execute(
        self: Self,
        key: str,
        expires_in: int = 1800,
    ) -> str:
        return await self.repository.generate(key, expires_in)
