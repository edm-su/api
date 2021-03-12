from typing import Optional, Mapping

from sqlalchemy import select

from app import db
from app.schemas import dj as dj_schema


async def find(id_: int = None, name: str = None) -> Optional[Mapping]:
    query = db.djs.select()
    if id_:
        query = query.where(db.djs.c.id == id_)
    if name:
        query = query.where(db.djs.c.name == name)
    query = query.limit(1)
    return await db.database.fetch_one(query)


async def create(new_dj: dj_schema.CreateDJ) -> Mapping:
    async with db.database.transaction():
        query = db.djs.insert().returning(db.djs)
        dj = await db.database.fetch_one(
            query,
            new_dj.dict(exclude={'group_members', }),
        )
        if new_dj.group_members:
            values = [
                {
                    'group_id': dj['id'],
                    'dj_id': group_member,
                } for group_member in new_dj.group_members]
            query = db.group_members.insert()
            query = query.values(values)
            query = query.returning(db.group_members.c.id)
            await db.database.execute(query)
    return dj


async def get_group_members(id_: int) -> Mapping:
    j = db.group_members.join(
        db.djs,
        db.group_members.c.dj_id == db.djs.c.id,
    )
    query = select([db.djs]).select_from(j)
    query = query.where(db.group_members.c.group_id == id_)
    return await db.database.fetch_all(query)
