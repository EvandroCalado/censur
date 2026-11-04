from uuid import UUID

from fastapi import APIRouter, UploadFile, status

from src.audio.censor import Censor
from src.audio.dependecies import AudioServiceDep
from src.audio.schemas import AudioRead
from src.user.dependecies import UserDep

router = APIRouter()
censor = Censor()


@router.post(
    '/', response_model=AudioRead, status_code=status.HTTP_201_CREATED
)
async def create_audio(
    audio_file: UploadFile, audio_service: AudioServiceDep, user: UserDep
):
    audio = await audio_service.create(audio_file, user)

    return audio


@router.get('/', response_model=list[AudioRead])
async def read_all(service: AudioServiceDep, user: UserDep):
    return user.audios


@router.get('/{id}', response_model=AudioRead)
async def read_one(id: UUID, audio_service: AudioServiceDep, user: UserDep):
    audio = await audio_service.read_one(id)

    return audio
