import typing
from datetime import datetime, timedelta

from app.db import users, database
from app.helpers import get_password_hash, generate_secret_code


async def create_user(username: str, email: str, password: str, is_admin: bool = False) -> typing.Mapping:
    hashed_password = get_password_hash(password)

    query = users.insert().returning(users)
    values = {'username': username, 'email': email, 'password': hashed_password}

    if is_admin:
        values['activation_code'] = ''
    return await database.fetch_one(query=query, values=values)


async def get_user_by_email(email: str) -> typing.Mapping:
    query = users.select().where(users.c.email == email)
    return await database.fetch_one(query=query)


async def get_user_by_username(username: str) -> typing.Mapping:
    query = users.select().where(users.c.username == username)
    return await database.fetch_one(query=query)


async def get_user_by_id(user_id: int) -> typing.Mapping:
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)


async def get_user_by_recovery_code(code: str) -> users:
    query = users.select()
    query = query.where(users.c.recovery_code == code)
    query = query.where(users.c.recovery_code_lifetime_end > datetime.now())
    return await database.fetch_one(query)


async def activate_user(code: str) -> bool:
    query = users.update().where(users.c.is_active == False).where(users.c.activation_code == code).returning(users)
    values = {'is_active': True, 'activation_code': ''}
    return bool(await database.execute(query=query, values=values))


async def generate_recovery_user_code(user_id: int) -> str:
    recovery_code = generate_secret_code()
    lifetime_end = datetime.now() + timedelta(hours=1)

    query = users.update().where(users.c.id == user_id)
    values = {'recovery_code': recovery_code, 'recovery_code_lifetime_end': lifetime_end}
    await database.execute(query=query, values=values)
    return recovery_code


async def change_password(user_id: int, password: str, recovery: bool = False) -> bool:
    query = users.update().where(users.c.id == user_id).returning(users)
    values = {'password': get_password_hash(password)}
    if recovery:
        values.update({'recovery_code': None, 'recovery_code_lifetime_end': None})
    return bool(await database.execute(query=query, values=values))
