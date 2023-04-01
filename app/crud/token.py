from collections.abc import Mapping

from app.db import database, users_tokens


async def add_token(name: str, token: str, user_id: int) -> None | Mapping:
    query = users_tokens.insert().returning(users_tokens.c.token)
    values = {"name": name, "token": token, "user_id": user_id}
    return await database.fetch_one(query, values)


async def find_token_by_name(name: str, user_id: int) -> None | Mapping:
    query = users_tokens.select().where(
        (users_tokens.c.name == name) & (users_tokens.c.user_id == user_id),
    )
    return await database.fetch_one(query)


async def find_token(token: str) -> None | Mapping:
    query = users_tokens.select().where(users_tokens.c.token == token)
    return await database.fetch_one(query)
