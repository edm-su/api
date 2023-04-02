from collections.abc import Mapping

from sqlalchemy import and_, func, select

from app import db
from app.schemas import dj as dj_schema


async def find(
    id_: int | None = None,  # noqa: ARG001
    name: str | None = None,  # noqa: ARG001
    slug: str | None = None,  # noqa: ARG001
) -> Mapping:
    conditions = []
    for key, value in locals().items():
        if value and key != "conditions":
            if key == "id_":
                key = "id"  # noqa: PLW2901
            conditions.append(db.djs.columns[key] == value)
    query = db.djs.select()
    query = query.where(and_(*conditions))
    query = query.limit(1)
    return await db.database.fetch_one(query)


async def create(new_dj: dj_schema.CreateDJ) -> Mapping:
    async with db.database.transaction():
        query = db.djs.insert().returning(db.djs)
        dj = await db.database.fetch_one(
            query,
            new_dj.dict(
                exclude={
                    "group_members",
                },
            ),
        )
        if new_dj.group_members:
            await add_group_members(dj["id"], new_dj.group_members)
    return dj


async def get_groups_members(ids: list[int]) -> Mapping:
    j = db.group_members.join(
        db.djs,
        db.group_members.c.dj_id == db.djs.c.id,
    )
    query = select([db.djs, db.group_members]).select_from(j)
    query = query.where(db.group_members.c.group_id.in_(ids))
    return await db.database.fetch_all(query)


async def get_members_of_groups(ids: list[int]) -> Mapping:
    j = db.group_members.join(
        db.djs,
        db.group_members.c.group_id == db.djs.c.id,
    )
    query = select([db.djs, db.group_members]).select_from(j)
    query = query.where(db.group_members.c.dj_id.in_(ids))
    return await db.database.fetch_all(query)


async def delete(id_: int) -> bool:
    query = db.djs.delete().where(db.djs.c.id == id_)
    return bool(await db.database.fetch_one(query))


async def count() -> int:
    query = select([func.count()]).select_from(db.djs)
    return await db.database.fetch_val(query)


async def get_list(skip: int = 0, limit: int = 0) -> Mapping:
    query = db.djs.select().order_by(db.djs.c.name).limit(limit).offset(skip)
    return await db.database.fetch_all(query)


async def update(id_: int, new_data: dj_schema.ChangeDJ) -> Mapping:
    data = new_data.dict(
        exclude_unset=True,
        exclude={"group_members"},
    )
    db_dj = await find(id_)
    async with db.database.transaction():
        if db_dj["is_group"] and not new_data.is_group:
            group_members = await get_groups_members([id_])
            await delete_group_members(
                [member["id"] for member in group_members],
            )
        elif db_dj["is_group"] or new_data.is_group and new_data.group_members:
            group_members = await get_groups_members([id_])
            members_ids = [member["dj_id"] for member in group_members]
            new_members = []
            for new_member in new_data.group_members:
                if new_member not in members_ids:
                    new_members.append(new_member)
            old_members = [
                member["id"]
                for member in group_members
                if member["dj_id"] not in new_data.group_members
            ]
            await delete_group_members(old_members)
            await add_group_members(id_, new_members)

        if data:
            query = db.djs.update().where(db.djs.c.id == id_).returning(db.djs)
        else:
            query = db.djs.select().where(db.djs.c.id == id_)
        return await db.database.fetch_one(query, data)


async def delete_group_members(ids: list[int]) -> bool:
    query = db.group_members.delete().where(db.group_members.c.dj_id.in_(ids))
    return bool(await db.database.fetch_val(query))


async def add_group_members(group_id: int, ids: list[int]) -> bool:
    values = [
        {
            "group_id": group_id,
            "dj_id": group_member,
        }
        for group_member in ids
    ]
    query = db.group_members.insert()
    query = query.values(values)
    query = query.returning(db.group_members.c.id)
    return bool(await db.database.execute(query))
