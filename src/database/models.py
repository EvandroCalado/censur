from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy.dialects import postgresql
from sqlmodel import Column, Field, Relationship, SQLModel


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
    sound_effects: list['SoundEffect'] = Relationship(
        back_populates='user', sa_relationship_kwargs={'lazy': 'selectin'}
    )


class SoundEffect(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    file_path: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    user_id: UUID = Field(foreign_key='user.id')
    user: User = Relationship(
        back_populates='sound_effects',
        sa_relationship_kwargs={'lazy': 'selectin'},
    )


class Audio(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    file_path: str
    censored_file_path: str | None = Field(default=None)
    status: AudioStatus = Field(default=AudioStatus.pending)
    transcription: list[dict] | None = Field(
        default=None, sa_column=Column(postgresql.JSONB)
    )
    user_beep: bool = Field(default=False)
    user_list: list[str] | None = Field(
        default=None, sa_column=Column(postgresql.ARRAY(postgresql.TEXT))
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={'onupdate': lambda: datetime.now(timezone.utc)},
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    user_id: UUID = Field(foreign_key='user.id')
    user: User = Relationship(
        back_populates='audios', sa_relationship_kwargs={'lazy': 'selectin'}
    )

    sound_effect_id: UUID | None = Field(
        default=None, foreign_key='sound_effect.id'
    )
    sound_effect: SoundEffect = Relationship(
        sa_relationship_kwargs={'lazy': 'selectin'}
    )
