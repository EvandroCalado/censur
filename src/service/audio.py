from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlmodel import Session

from src.audio_censor import AudioCensor
from src.database.models import Audio
from src.utils import get_file_path, save_file


class AudioService:
    def __init__(self, session: Session):
        self.session = session
        self.ac = AudioCensor()

    def create_audio(self, file: UploadFile) -> Audio:
        file_path = save_file(file)
        output_path = get_file_path(f'censored_{file.filename}')

        audio = Audio(
            file_path=str(file.filename), censored_file_path=output_path
        )

        self.session.add(audio)
        self.session.commit()
        self.session.refresh(audio)

        words = self.ac.transcribe_audio(file_path)
        self.ac.mute_audio(
            input_path=file_path,
            output_path=output_path,
            word_segments=self.ac.detect_profanity(words),
        )

        return audio

    def read_one_audio(self, id: UUID) -> Audio:
        audio = self.session.get(Audio, id)

        if audio is None:
            raise HTTPException(
                detail='Audio not found',
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return audio
