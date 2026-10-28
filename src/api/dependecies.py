from typing import Annotated

from fastapi import Depends

from src.database.session import SessionDep
from src.service.audio import AudioService


def get_audio_service(session: SessionDep) -> AudioService:
    return AudioService(session)


AudioServiceDep = Annotated[AudioService, Depends(get_audio_service)]
