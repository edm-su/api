import pytest
from faker import Faker
from fastapi import status
from httpx import AsyncClient
from pytest_mock import MockerFixture
from typing_extensions import Self

from edm_su_api.internal.controller.http.v1.upload import (
    PreSignedUploadResponse,
)

pytestmark = pytest.mark.anyio


class TestGeneratePreSignedURL:
    @pytest.mark.usefixtures("mock_current_user")
    async def test_generate_pre_signed_url(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
        faker: Faker,
    ) -> None:
        url = faker.url()
        mocked = mocker.patch(
            "edm_su_api.internal.usecase.upload.GeneratePreSignedUploadUseCase.execute",
            return_value=url,
        )
        response = await client.get(
            "/upload/pre_signed",
            params={"key": faker.file_path(depth=3, category="image")},
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_200_OK
        response_data = PreSignedUploadResponse.model_validate(response.json())
        assert str(response_data.url) == url

    async def test_unauthorized(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
        faker: Faker,
    ) -> None:
        mocked = mocker.patch(
            "edm_su_api.internal.usecase.upload.GeneratePreSignedUploadUseCase.execute",
            return_value=faker.url(),
        )
        response = await client.get(
            "/upload/pre_signed",
        )

        mocked.assert_not_awaited()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
