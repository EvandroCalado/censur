from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from src.user.dependecies import UserServiceDep
from src.user.schemas import Token, UserCreate, UserRead

router = APIRouter()


@router.post(
    '/signup', response_model=UserRead, status_code=status.HTTP_201_CREATED
)
async def register_user(user_create: UserCreate, user_service: UserServiceDep):
    user = await user_service.register_user(user_create)

    return user


@router.post('/token', response_model=Token)
async def login_user(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: UserServiceDep,
):
    user = await user_service.login_user(
        credentials.username, credentials.password
    )

    access_token = user_service.create_access_token(user)

    return {
        'access_token': access_token,
        'token_type': 'bearer',
    }
