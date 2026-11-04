from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.config import settings
from src.database.models import User
from src.database.session import SessionDep
from src.user.services import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/user/token')


def get_user_service(session: SessionDep) -> UserService:
    return UserService(session)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.PyJWTError:
        raise HTTPException(
            detail='Invalid or expired token',
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={'WWW-Authenticate': 'Bearer'},
        )

    user_id = UUID(payload.get('sub'))
    user = await service.get_user(user_id)

    if user is None:
        raise HTTPException(
            detail='User not found',
            status_code=status.HTTP_404_NOT_FOUND,
            headers={'WWW-Authenticate': 'Bearer'},
        )

    return user


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
UserDep = Annotated[User, Depends(get_current_user)]
