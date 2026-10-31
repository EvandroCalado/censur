from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.audio_censor import AudioCensor
from src.database.models import Audio
from src.utils import get_file_path, save_file


class AudioService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.ac = AudioCensor()

    async def create_audio(self, file: UploadFile) -> Audio:
        file_path = save_file(file)
        output_path = get_file_path(f'censored_{file.filename}')

        audio = Audio(
            file_path=str(file.filename), censored_file_path=output_path
        )

        self.session.add(audio)
        await self.session.commit()
        await self.session.refresh(audio)

        words = self.ac.transcribe_audio(file_path)
        self.ac.mute_audio(
            input_path=file_path,
            output_path=output_path,
            word_segments=self.ac.detect_profanity(words),
        )

        return audio

    async def read_one_audio(self, id: UUID) -> Audio:
        audio = await self.session.get(Audio, id)

        if audio is None:
            raise HTTPException(
                detail='Audio not found',
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return audio
