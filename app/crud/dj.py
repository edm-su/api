from typing import Optional, Mapping

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


async def create(new_dj: dj_schema.CreateDJ) -> Optional[Mapping]:
    query = db.djs.insert().returning(db.djs)
    return await db.database.fetch_one(query, new_dj.dict())
