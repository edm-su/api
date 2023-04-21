import hashlib
import os
from abc import ABC, abstractmethod
from io import BytesIO
from typing import IO

import httpx
from PIL import Image
from typing_extensions import Self

from app.internal.entity.upload import ImageURL, ImageURLs
from app.internal.usecase.exceptions.upload import (
    FileIsNotImageError,
    FileIsTooLargeError,
)
from app.internal.usecase.repository.upload import AbstractUploadRepository
from app.settings import settings

MAX_FILE_SIZE = 5_000_000


class ImageConverter(ABC):
    extension: str

    def __init__(
        self: Self,
        file: IO[bytes],
    ) -> None:
        self.file = file
        self.converted_file = None

    def convert(self: Self) -> None:
        raise NotImplementedError


class JPEGImageConverter(ImageConverter):
    extension = "jpeg"

    def convert(self: Self) -> None:
        image = Image.open(self.file)
        image = image.convert("RGB")
        jpeg_image = BytesIO()
        image.save(jpeg_image, "JPEG")
        jpeg_image.seek(0)
        self.converted_file = jpeg_image  # type: ignore[assignment]


class BaseUploadUseCase(ABC):
    def __init__(
        self: Self,
        repository: AbstractUploadRepository,
        file: IO[bytes],
    ) -> None:
        self.repository = repository
        self.file = file

    @abstractmethod
    async def execute(self: Self) -> ImageURLs:
        pass

    def _get_sha256_hash(self: Self) -> str:
        sha256 = hashlib.sha256()
        self.file.seek(0)
        while chunk := self.file.read(8192):
            sha256.update(chunk)
        return sha256.hexdigest()

    def _get_file_size(self: Self) -> int:
        self.file.seek(0, os.SEEK_END)
        size = self.file.tell()
        self.file.seek(0)
        return size


class UploadImageUseCase(BaseUploadUseCase):
    async def execute(self: Self) -> ImageURLs:
        if self._get_file_size() > MAX_FILE_SIZE:
            raise FileIsTooLargeError(self._get_file_size(), MAX_FILE_SIZE)

        converters = [JPEGImageConverter(self.file)]
        base_path = "images"
        md5 = self._get_sha256_hash()
        for converter in converters:
            path = f"{base_path}/{md5}.{converter.extension}"
            converter.convert()
            if converter.converted_file is None:
                raise FileIsNotImageError
            await self.repository.upload(converter.converted_file, path)

        result = {}
        for converter in converters:
            path = (
                f"{settings.static_url}/{base_path}"
                f"/{md5}.{converter.extension}"
            )
            result[converter.extension] = path
        return ImageURLs.parse_obj(result)


class UploadImageURLUseCase(UploadImageUseCase):
    def __init__(
        self: Self,
        repository: AbstractUploadRepository,
        image_url: ImageURL,
    ) -> None:
        self.repository = repository
        self.image_url = image_url

    async def execute(self: Self) -> ImageURLs:
        async with httpx.AsyncClient() as client:
            h = await client.head(self.image_url.url)
            header = h.headers
        if not header.get("Content-Type").startswith("image/"):
            raise FileIsNotImageError

        if int(header.get("Content-Length")) > MAX_FILE_SIZE:
            raise FileIsTooLargeError(
                int(header.get("Content-Length")),
                MAX_FILE_SIZE,
            )

        async with httpx.AsyncClient() as client:
            r = await client.get(self.image_url.url)
            image = BytesIO(r.content)

        self.file = image
        return await super().execute()
