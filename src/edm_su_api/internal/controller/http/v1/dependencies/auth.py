from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from edm_su_api.internal.entity.user import User


async def get_current_user(
    x_user: Annotated[str | None, Header()] = None,
) -> User:
    if x_user:
        return User(id=x_user)
    raise HTTPException(status.HTTP_401_UNAUTHORIZED)


CurrentUser = Annotated[User, Depends(get_current_user)]
