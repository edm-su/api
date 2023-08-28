from typing import Annotated

from fastapi import Depends

from app.internal.usecase.repository.permission import (
    SpiceDBPermissionRepository,
)
from app.pkg.authzed import get_spicedb_client


async def create_spicedb_repository() -> SpiceDBPermissionRepository:
    return SpiceDBPermissionRepository(await get_spicedb_client())


SpiceDBPermissionsRepo = Annotated[
    SpiceDBPermissionRepository,
    Depends(create_spicedb_repository),
]
