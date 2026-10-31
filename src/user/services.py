import datetime

import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.config import settings
from src.database.models import User
from src.user.schemas import UserCreate


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.pwd_context = CryptContext(schemes=['argon2'], deprecated='auto')

    async def register_user(self, user_create: UserCreate) -> User:
        existing_user = await self.session.execute(
            select(User).where(User.email == user_create.email)
        )

        if existing_user.first() is not None:
            raise HTTPException(
                detail='User already registered!',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user = User(
            email=user_create.email,
            password_hash=self.pwd_context.hash(user_create.password),
        )

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def login_user(self, email: str, password: str) -> User:
        user = await self.session.scalar(
            select(User).where(User.email == email)
        )

        if user is None:
            raise HTTPException(
                detail='Invalid credentials',
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        if not self.pwd_context.verify(password, user.password_hash):
            raise HTTPException(
                detail='Invalid credentials',
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        return user

    @staticmethod
    def create_access_token(user: User) -> str:
        now = datetime.datetime.now(datetime.timezone.utc)
        payload = {
            'sub': str(user.id),
            'exp': now + datetime.timedelta(minutes=15),
        }

        return jwt.encode(
            payload,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )
