from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


class AudioStatus(Enum):
    pending = 'pending'
    processing = 'processing'
    completed = 'completed'
    failed = 'failed'


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str
    password_hash: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    audios: list['Audio'] = Relationship(
        back_populates='user', sa_relationship_kwargs={'lazy': 'selectin'}
    )


class Audio(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    file_path: str
    censored_file_path: str | None = Field(default=None)
    status: AudioStatus = Field(default=AudioStatus.pending)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    user_id: UUID = Field(foreign_key='user.id')
    user: User = Relationship(
        back_populates='audios', sa_relationship_kwargs={'lazy': 'selectin'}
    )
