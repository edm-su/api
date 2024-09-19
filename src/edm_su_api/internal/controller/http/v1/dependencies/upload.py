from fastapi import Depends
from types_aiobotocore_s3.client import S3Client

from edm_su_api.internal.usecase.repository.upload import (
    S3PreSignedUploadRepository,
)
from edm_su_api.internal.usecase.upload import GeneratePreSignedUploadUseCase
from edm_su_api.pkg.s3 import get_s3_client


def create_pre_signed_upload_pepository(
    s3_client: S3Client = Depends(get_s3_client),
) -> S3PreSignedUploadRepository:
    return S3PreSignedUploadRepository(s3_client)


def create_generate_pre_signed_upload_use_case(
    repo: S3PreSignedUploadRepository = Depends(
        create_pre_signed_upload_pepository
    ),
) -> GeneratePreSignedUploadUseCase:
    return GeneratePreSignedUploadUseCase(repo)
