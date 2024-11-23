from unittest.mock import AsyncMock

import pytest
from typing_extensions import Self

from edm_su_api.internal.usecase.repository.upload import (
    AbstractPreSignedUploadRepository,
)
from edm_su_api.internal.usecase.upload import (
    GeneratePreSignedUploadUseCase,
)

pytestmark = pytest.mark.anyio


class TestGeneratePreSignedUploadUseCase:
    @pytest.fixture
    def repository(self: Self) -> AbstractPreSignedUploadRepository:
        return AsyncMock(spec=AbstractPreSignedUploadRepository)

    @pytest.fixture
    def usecase(
        self: Self,
        repository: AsyncMock,
    ) -> GeneratePreSignedUploadUseCase:
        return GeneratePreSignedUploadUseCase(repository)

    async def test_generate_pre_signed_url(
        self: Self,
        usecase: GeneratePreSignedUploadUseCase,
        repository: AsyncMock,
    ) -> None:
        key = "test_key"
        expires_in = 1800
        expected_url = "https://pre-signed-url.com"

        repository.generate.return_value = expected_url

        result = await usecase.execute(key, expires_in)

        assert result == expected_url
        repository.generate.assert_awaited_once_with(key, expires_in)
