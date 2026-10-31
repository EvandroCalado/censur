from typing import Annotated

from fastapi import Depends

from src.audio.services import AudioService
from src.database.session import SessionDep


def get_audio_service(session: SessionDep) -> AudioService:
    return AudioService(session)


AudioServiceDep = Annotated[AudioService, Depends(get_audio_service)]
