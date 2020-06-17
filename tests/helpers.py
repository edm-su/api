import typing

from app.auth import create_access_token


def create_auth_header(username) -> typing.Mapping:
    token = create_access_token(data={'sub': username}).decode('utf-8')
    return {'Authorization': f'Bearer {token}'}
