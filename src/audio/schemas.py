from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.database.models import AudioStatus


class AudioRead(BaseModel):
    id: UUID
    censored_file_path: str | None
    status: AudioStatus
    created_at: datetime
