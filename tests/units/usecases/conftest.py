from unittest.mock import AsyncMock

import pytest

from app.internal.usecase.repository.permission import (
    AbstractPermissionRepository,
)


@pytest.fixture()
def permissions_repo() -> AbstractPermissionRepository:
    return AsyncMock(repr=AbstractPermissionRepository)
