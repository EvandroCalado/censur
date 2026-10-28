from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile
from sqlmodel import Session

from src.audio_censor import AudioCensor
from src.database.session import get_session
from src.service.audio import AudioService

router = APIRouter()
ac = AudioCensor()


@router.post('/')
def censor_audio(
    audio_file: UploadFile, session: Annotated[Session, Depends(get_session)]
):
    audio = AudioService(session).add_audio(audio_file)

    return {
        'id': audio.id,
        'url': f'/uploads/censored_{audio_file.filename}',
    }


# @router.get('/{id}')
# def get_audio(id: int, session: Annotated[Session, Depends(get_session)]):
#     audio = session.get(Audio, id)
#     return {
#         'id': audio.id,
#         'file_path': audio.file_path,
#         'censored_file_path': audio.censored_file_path,
#     }


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
