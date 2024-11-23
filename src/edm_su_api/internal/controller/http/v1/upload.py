from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field, HttpUrl, TypeAdapter

from edm_su_api.internal.controller.http.v1.dependencies.auth import (
    CurrentUser,
)
from edm_su_api.internal.controller.http.v1.dependencies.upload import (
    create_generate_pre_signed_upload_use_case,
)
from edm_su_api.internal.usecase.upload import (
    GeneratePreSignedUploadUseCase,
)

router = APIRouter(tags=["Upload"])


class PreSignedUploadParams(BaseModel):
    key: str = Field(default_factory=lambda: f"{uuid4()!s}.png")
    expires_in: int = Field(1800, ge=60, le=3600)


class PreSignedUploadResponse(BaseModel):
    url: HttpUrl


@router.get(
    path="/pre_signed",
    summary="Get pre-signed url for file uploads",
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
