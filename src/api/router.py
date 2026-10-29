from uuid import UUID

from fastapi import APIRouter, UploadFile, status

from src.api.dependecies import AudioServiceDep
from src.api.schemas import AudioRead
from src.audio_censor import AudioCensor

router = APIRouter()
ac = AudioCensor()


@router.post(
    '/', response_model=AudioRead, status_code=status.HTTP_201_CREATED
)
async def create_audio(audio_file: UploadFile, audio_service: AudioServiceDep):
    audio = await audio_service.create_audio(audio_file)

    return audio


@router.get('/{id}', response_model=AudioRead)
async def read_audio(id: UUID, audio_service: AudioServiceDep):
    audio = await audio_service.read_one_audio(id)

    return audio


# @router.patch('/{id}')
# def update_audio(
#     id: int,
#     audio_file: UploadFile,
#     session: Annotated[Session, Depends(get_session)],
# ):
#     file_path = f'{UPLOADS_DIR}/{audio_file.filename}'
#     output_path = f'{UPLOADS_DIR}/censored_{audio_file.filename}'

#     audio = session.get(Audio, id)
#     audio.file_path = file_path
#     audio.censored_file_path = output_path
#     session.commit()

#     return {'url': f'/uploads/censored_{audio_file.filename}'}


# @router.delete('/{id}')
# def delete_audio(
#     id: int,
#     session: Annotated[Session, Depends(get_session)],
# ):
#     audio = session.get(Audio, id)
#     session.deleted(audio)
#     session.commit()

#     return {'message': f'Audio with id {id} deleted successfully.'}
