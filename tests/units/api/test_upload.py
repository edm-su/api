import io
from typing import IO

import pytest
from faker import Faker
from fastapi import status
from httpx import AsyncClient
from pytest_mock import MockerFixture
from typing_extensions import Self

from edm_su_api.internal.controller.http.v1.upload import (
    PreSignedUploadResponse,
)
from edm_su_api.internal.entity.upload import ImageURLs
from edm_su_api.internal.usecase.exceptions.upload import (
    FileIsNotImageError,
    FileIsTooLargeError,
)

pytestmark = pytest.mark.anyio


@pytest.fixture
def image_urls(
    faker: Faker,
) -> ImageURLs:
    return ImageURLs.model_validate(
        {
            "jpeg": faker.url(),
        },
    )


UploadImage = tuple[str, IO[bytes], str]


@pytest.fixture
def image(image: IO[bytes]) -> UploadImage:
    return "test.jpeg", image, "image/jpeg"


class TestUpload:
    @pytest.mark.usefixtures("mock_current_user")
    async def test_upload_image(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
        image: UploadImage,
        image_urls: ImageURLs,
    ) -> None:
        mocked = mocker.patch(
            "edm_su_api.internal.usecase.upload.UploadImageUseCase.execute",
            return_value=image_urls,
        )
        response = await client.post(
            "/upload/images",
            files={"image": image},
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_200_OK
        assert ImageURLs.model_validate(response.json()) == image_urls

    @pytest.mark.usefixtures("mock_current_user")
    async def test_upload_error(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
        image: UploadImage,
    ) -> None:
        mocked = mocker.patch(
            "edm_su_api.internal.usecase.upload.UploadImageUseCase.execute",
            side_effect=FileIsTooLargeError(2, 1),
        )
        response = await client.post(
            "/upload/images",
            files={"image": image},
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE

    @pytest.mark.usefixtures("mock_current_user")
    async def test_upload_not_image(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
        image: UploadImage,
    ) -> None:
        buffer_size = 5 * 1024 * 1024 + 1
        buffer = io.BytesIO(b"\x00" * buffer_size)
        response = await client.post(
            "/upload/images",
            files={"image": buffer},
        )

        assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

        mocked = mocker.patch(
            "edm_su_api.internal.usecase.upload.UploadImageUseCase.execute",
            side_effect=FileIsNotImageError,
        )
        response = await client.post(
            "/upload/images",
            files={"image": image},
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestUploadImageURL:
    @pytest.mark.usefixtures("mock_current_user")
    async def test_upload_image_by_url(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
        image_urls: ImageURLs,
        faker: Faker,
    ) -> None:
        mocked = mocker.patch(
            "edm_su_api.internal.usecase.upload.UploadImageURLUseCase.execute",
            return_value=image_urls,
        )
        response = await client.post(
            "/upload/image_url",
            json={"url": faker.url()},
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_200_OK
        assert ImageURLs.model_validate(response.json()) == image_urls

    @pytest.mark.usefixtures("mock_current_user")
    async def test_upload_error(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
        faker: Faker,
    ) -> None:
        mocked = mocker.patch(
            "edm_su_api.internal.usecase.upload.UploadImageURLUseCase.execute",
            side_effect=FileIsTooLargeError(2, 1),
        )
        response = await client.post(
            "/upload/image_url",
            json={"url": faker.url()},
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE

        mocked = mocker.patch(
            "edm_su_api.internal.usecase.upload.UploadImageURLUseCase.execute",
            side_effect=FileIsNotImageError,
        )
        response = await client.post(
            "/upload/image_url",
            json={"url": faker.url()},
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_400_BAD_REQUEST


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
        assert (
            str(PreSignedUploadResponse.model_validate(response.json()).url)
            == url
        )

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
