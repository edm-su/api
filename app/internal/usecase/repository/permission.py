from abc import ABC, abstractmethod
from typing import NamedTuple

from authzed.api.v1 import (
    Client,
    DeleteRelationshipsRequest,
    ObjectReference,
    Relationship,
    RelationshipFilter,
    RelationshipUpdate,
    SubjectFilter,
    SubjectReference,
    WriteRelationshipsRequest,
)
from typing_extensions import Self


class Object(NamedTuple):
    object_type: str
    object_id: str


class AbstractPermissionRepository(ABC):
    @abstractmethod
    async def write(
        self: Self,
        resource: Object,
        relation: str,
        subject: Object,
        subject_relation: str = "",
    ) -> None:
        pass

    @abstractmethod
    async def delete(
        self: Self,
        resource: Object,
        relation: str | None = None,
        subject: Object | None = None,
        subject_relation: str | None = None,
    ) -> None:
        pass


class SpiceDBPermissionRepository(AbstractPermissionRepository):
    def __init__(self: Self, client: Client) -> None:
        self.client = client

    async def write(
        self: Self,
        resource: Object,
        relation: str,
        subject: Object,
        subject_relation: str = "",
    ) -> None:
        _resource = ObjectReference(
            object_type=resource.object_type,
            object_id=resource.object_id,
        )
        _subject = SubjectReference(
            object=ObjectReference(
                object_type=subject.object_type,
                object_id=subject.object_id,
            ),
            optional_relation=subject_relation,
        )

        await self.client.WriteRelationships(
            WriteRelationshipsRequest(
                updates=[
                    RelationshipUpdate(
                        operation=RelationshipUpdate.Operation.OPERATION_CREATE,
                        relationship=Relationship(
                            resource=_resource,
                            subject=_subject,
                            relation=relation,
                        ),
                    ),
                ],
            ),
        )

    async def delete(
        self: Self,
        resource: Object,
        relation: str | None = None,
        subject: Object | None = None,
        subject_relation: str | None = None,
    ) -> None:
        subject_filter = self._build_subject_filter(subject, subject_relation)

        relationship_filter = self._build_relationship_filter(
            resource,
            subject_filter,
            relation,
        )

        await self.client.DeleteRelationships(
            DeleteRelationshipsRequest(
                relationship_filter=relationship_filter,
            ),
        )

    def _build_relationship_filter(
        self: Self,
        resource: Object,
        subject_filter: SubjectFilter | None,
        relation: str | None,
    ) -> RelationshipFilter:
        relationship = RelationshipFilter(
            resource_type=resource.object_type,
            optional_resource_id=resource.object_id,
            optional_subject_filter=subject_filter,
        )
        if relation:
            relationship.optional_relation = relation
        return relationship

    def _build_subject_filter(
        self: Self,
        subject: Object | None,
        subject_relation: str | None,
    ) -> SubjectFilter | None:
        if subject:
            subject_relation_filter = None
            if subject_relation:
                subject_relation_filter = SubjectFilter.RelationFilter(
                    relation=subject_relation,
                )

            return SubjectFilter(
                subject_type=subject.object_type,
                optional_subject_id=subject.object_id,
                optional_relation=subject_relation_filter,
            )
        return None
