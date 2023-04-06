from app.auth import create_token


def create_auth_header(username: str) -> dict[str, str]:
    token = create_token(data={"sub": username})
    return {"Authorization": f"Bearer {token}"}
