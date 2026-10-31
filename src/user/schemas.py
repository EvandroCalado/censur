from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: UUID
    email: str
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'
