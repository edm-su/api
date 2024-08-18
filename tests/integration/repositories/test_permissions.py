import pytest
from authzed.api.v1 import Client, WriteSchemaRequest
from typing_extensions import Self

from edm_su_api.internal.usecase.repository.permission import (
    Object,
    SpiceDBPermissionRepository,
)
from edm_su_api.pkg.authzed import get_spicedb_client


@pytest.fixture(scope="session")
async def spicedb_client() -> Client:
    return await get_spicedb_client()


@pytest.fixture(autouse=True, scope="session")
async def write_spicedb_schema(spicedb_client: Client) -> None:
    schema = """definition user {}

    definition resource {
        relation tester: user

        permission test = tester
    }"""

    await spicedb_client.WriteSchema(WriteSchemaRequest(schema=schema))


class TestSpiceDBPermissionsRepository:
    @pytest.fixture
    def repo(
        self: Self,
        spicedb_client: Client,
    ) -> SpiceDBPermissionRepository:
        return SpiceDBPermissionRepository(client=spicedb_client)

    @pytest.fixture
    def resource(self: Self) -> Object:
        return Object(object_type="resource", object_id="test")

    @pytest.fixture
    def relation(self: Self) -> str:
        return "tester"

    @pytest.fixture
    def subject(self: Self) -> Object:
        return Object(object_type="user", object_id="test")

    async def test_write(
        self: Self,
        repo: SpiceDBPermissionRepository,
        resource: Object,
        relation: str,
        subject: Object,
    ) -> None:
        await repo.write(
            resource,
            relation,
            subject,
        )

    async def test_delete(
        self: Self,
        repo: SpiceDBPermissionRepository,
        resource: Object,
        relation: str,
        subject: Object,
    ) -> None:
        await repo.delete(
            resource,
            relation,
            subject,
        )
