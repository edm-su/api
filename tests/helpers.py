from app.auth import create_access_token


def create_auth_header(username: str) -> dict[str, str]:
    token = create_access_token(data={'sub': username})
    return {'Authorization': f'Bearer {token}'}
