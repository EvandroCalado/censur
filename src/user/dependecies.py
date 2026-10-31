from typing import Annotated

from fastapi import Depends

from src.database.session import SessionDep
from src.user.services import UserService


def get_user_service(session: SessionDep) -> UserService:
    return UserService(session)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
