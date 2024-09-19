from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field, HttpUrl, TypeAdapter
from starlette import status
from types_aiobotocore_s3.client import S3Client

from edm_su_api.internal.controller.http.v1.dependencies.auth import (
    CurrentUser,
)
from edm_su_api.internal.controller.http.v1.dependencies.upload import (
    create_generate_pre_signed_upload_use_case,
)
from edm_su_api.internal.entity.upload import ImageURL, ImageURLs
from edm_su_api.internal.usecase.exceptions.upload import (
    FileIsTooLargeError,
    UploadError,
)
from edm_su_api.internal.usecase.repository.upload import S3UploadRepository
from edm_su_api.internal.usecase.upload import (
    GeneratePreSignedUploadUseCase,
    UploadImageURLUseCase,
    UploadImageUseCase,
)
from edm_su_api.pkg.s3 import get_s3_client

router = APIRouter(tags=["Upload"])


@router.post(
    "/images",
    summary="Upload image",
    response_model=ImageURLs,
    deprecated=True,
)
async def upload_image(
    image: Annotated[
        UploadFile,
        File,
    ],
    s3_client: S3Client = Depends(get_s3_client),
) -> ImageURLs:
    if image.content_type is None or not image.content_type.startswith(
        "image/",
    ):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported media type",
        )

    use_case = UploadImageUseCase(S3UploadRepository(s3_client), image.file)
    try:
        urls = await use_case.execute()
    except FileIsTooLargeError as e:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(e),
        ) from e
    except UploadError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    return urls


@router.post(
    "/image_url",
    summary="Upload image by url",
    response_model=ImageURLs,
    deprecated=True,
)
async def upload_image_url(
    image_url: ImageURL,
    s3_client: S3Client = Depends(get_s3_client),
) -> ImageURLs:
    use_case = UploadImageURLUseCase(S3UploadRepository(s3_client), image_url)
    try:
        urls = await use_case.execute()
    except FileIsTooLargeError as e:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(e),
        ) from e
    except UploadError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    return urls


class PreSignedUploadParams(BaseModel):
    key: str = Field(default_factory=lambda: f"{uuid4()!s}.png")
    expires_in: int = Field(1800, ge=60, le=3600)


class PreSignedUploadResponse(BaseModel):
    url: HttpUrl


@router.get(
    path="/pre_signed",
    summary="Get pre-signed url for file uploads",
    response_model=PreSignedUploadResponse,
)
async def generate_pre_signed_upload(
    query: Annotated[PreSignedUploadParams, Query()],
    use_case: Annotated[
        GeneratePreSignedUploadUseCase,
        Depends(create_generate_pre_signed_upload_use_case),
    ],
    _: CurrentUser,
) -> PreSignedUploadResponse:
    url_str = await use_case.execute(query.key, query.expires_in)
    url = TypeAdapter(HttpUrl).validate_python(url_str)
    return PreSignedUploadResponse(url=url)
