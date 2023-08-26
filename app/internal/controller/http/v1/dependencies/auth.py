from typing import Annotated

from fastapi import Depends, Header

from app.internal.entity.user import User


async def get_current_user(x_user: Annotated[str, Header()]) -> User:
    return User(id=x_user)


CurrentUser = Annotated[User, Depends(get_current_user)]
