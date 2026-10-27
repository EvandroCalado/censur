import warnings
from pathlib import Path
from typing import NotRequired, TypedDict

import whisperx
from better_profanity import profanity
from pydub import AudioSegment
from pydub.generators import Sine

warnings.filterwarnings('ignore')


class Word(TypedDict):
    word: str
    start: float
    end: float
    score: float
    flagged: NotRequired[bool]


class AudioCensor:
    def __init__(
        self,
        model_name: str = 'small',
        device: str = 'cpu',
        compute_type: str = 'int8',
        language: str = 'en',
    ):
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type
        self.language = language

        self.model = whisperx.load_model(
            self.model_name,
            device=self.device,
            compute_type=self.compute_type,
            language=self.language,
        )
        self.align_model, self.align_metadata = whisperx.load_align_model(
            language_code=self.language, device=self.device
        )

        profanity.load_censor_words()

    def transcribe_audio(self, audio_path: str) -> list[Word]:
        audio = whisperx.load_audio(audio_path)

        result = self.model.transcribe(
            audio, batch_size=16, language=self.language
        )

        aligned_result = whisperx.align(
            result['segments'],
            self.align_model,
            self.align_metadata,
            audio,
            self.device,
            return_char_alignments=False,
        )

        return aligned_result['word_segments']

    @staticmethod
    def detect_profanity(word_segments: list[Word]) -> list[Word]:
        for segment in word_segments:
            word_text = segment.get('word', '')
            segment['flagged'] = profanity.contains_profanity(word_text)
        return word_segments

    @staticmethod
    def mute_audio(
        input_path: str,
        output_path: str,
        word_segments: list[Word],
        beep: bool = False,
    ) -> None:
        audio = AudioSegment.from_file(input_path)

        for segment in word_segments:
            if segment.get('flagged', False):
                start_ms = int(segment.get('start', 0) * 1000)
                end_ms = int(segment.get('end', 0) * 1000)

                # Ensure the time bounds are valid within the audio duration
                start_ms = max(0, start_ms)
                end_ms = min(len(audio), end_ms)

                if start_ms < end_ms:
                    duration = end_ms - start_ms
                    if beep:
                        replacement = (
                            Sine(1000)
                            .to_audio_segment(duration=duration)
                            .apply_gain(-6)
                        )
                    else:
                        replacement = AudioSegment.silent(duration=duration)
                    audio = audio[:start_ms] + replacement + audio[end_ms:]

        output_format = Path(output_path).suffix.lstrip('.').lower() or 'wav'
        audio.export(output_path, format=output_format)
