from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AudioRead(BaseModel):
    id: UUID
    censored_file_path: str
    created_at: datetime
