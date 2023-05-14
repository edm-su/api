import io
from pathlib import Path

import pytest
from faker import Faker
from fastapi import status
from httpx import AsyncClient
from pytest_mock import MockerFixture
from typing_extensions import Self

from app.internal.entity.upload import ImageURLs
from app.internal.usecase.exceptions.upload import (
    FileIsNotImageError,
    FileIsTooLargeError,
)


@pytest.fixture()
def image_urls(
    faker: Faker,
) -> ImageURLs:
    return ImageURLs.parse_obj(
        {
            "jpeg": faker.url(),
        },
    )


class TestUpload:
    @pytest.mark.usefixtures("_mock_current_admin")
    async def test_upload_image(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
        image_urls: ImageURLs,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.upload.UploadImageUseCase.execute",
            return_value=image_urls,
        )
        path = Path("tests/files/test.jpeg")
        response = await client.post(
            "/upload/images",
            files={"image": path.open("rb")},
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == image_urls

    @pytest.mark.usefixtures("_mock_current_admin")
    async def test_upload_error(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.upload.UploadImageUseCase.execute",
            side_effect=FileIsTooLargeError(2, 1),
        )
        path = Path("tests/files/test.jpeg")
        response = await client.post(
            "/upload/images",
            files={"image": path.open("rb")},
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE

    @pytest.mark.usefixtures("_mock_current_admin")
    async def test_upload_not_image(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
    ) -> None:
        buffer_size = 5 * 1024 * 1024 + 1
        buffer = io.BytesIO(b"\x00" * buffer_size)
        response = await client.post(
            "/upload/images",
            files={"image": buffer},
        )

        assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

        mocked = mocker.patch(
            "app.internal.usecase.upload.UploadImageUseCase.execute",
            side_effect=FileIsNotImageError,
        )
        path = Path("tests/files/test.jpeg")
        response = await client.post(
            "/upload/images",
            files={"image": path.open("rb")},
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.usefixtures("_mock_current_user")
    async def test_without_permission(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
    ) -> None:
        path = Path("tests/files/test.jpeg")
        response = await client.post(
            "/upload/images",
            files={"image": path.open("rb")},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestUploadImageURL:
    @pytest.mark.usefixtures("_mock_current_admin")
    async def test_upload_image_by_url(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
        image_urls: ImageURLs,
        faker: Faker,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.upload.UploadImageURLUseCase.execute",
            return_value=image_urls,
        )
        response = await client.post(
            "/upload/image_url",
            json={"url": faker.url()},
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == image_urls

    @pytest.mark.usefixtures("_mock_current_admin")
    async def test_upload_error(
        self: Self,
        client: AsyncClient,
        mocker: MockerFixture,
        faker: Faker,
    ) -> None:
        mocked = mocker.patch(
            "app.internal.usecase.upload.UploadImageURLUseCase.execute",
            side_effect=FileIsTooLargeError(2, 1),
        )
        response = await client.post(
            "/upload/image_url",
            json={"url": faker.url()},
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE

        mocked = mocker.patch(
            "app.internal.usecase.upload.UploadImageURLUseCase.execute",
            side_effect=FileIsNotImageError,
        )
        response = await client.post(
            "/upload/image_url",
            json={"url": faker.url()},
        )

        mocked.assert_awaited_once()
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.usefixtures("_mock_current_user")
    async def test_without_permission(
        self: Self,
        client: AsyncClient,
        faker: Faker,
    ) -> None:
        response = await client.post(
            "/upload/image_url",
            json={"url": faker.url()},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
