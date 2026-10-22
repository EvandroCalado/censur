from typing import NotRequired, TypedDict

import whisperx
from better_profanity import profanity
from rich import print_json


class Word(TypedDict):
    word: str
    start: float
    end: float
    score: float
    flagged: NotRequired[bool]


class AudioCensor:
    def __init__(
        self,
        model_name: str = "small",
        device: str = "cpu",
        compute_type: str = "int8",
        language: str = "en",
    ):
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type
        self.language = language

        # Load models once and store them as attributes
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

    def transcribe_audio(self, audio_path: str) -> list[dict]:
        """
        Transcribes audio using WhisperX on CPU with English language setting,
        and performs forced alignment to return word/segment timestamps.
        """
        # 1. Load audio
        audio = whisperx.load_audio(audio_path)

        # 2. Transcribe with Whisper
        result = self.model.transcribe(audio, batch_size=16, language=self.language)

        # 3. Align whisper output using preloaded align model
        aligned_result = whisperx.align(
            result["segments"],
            self.align_model,
            self.align_metadata,
            audio,
            self.device,
            return_char_alignments=False,
        )

        return aligned_result["word_segments"]

    def detect_profanity(self, word_segments: list[dict]) -> list[dict]:
        """
        Detects profanity for each word segment using better_profanity,
        setting the 'flagged' key on each word dict.
        """
        for segment in word_segments:
            word_text = segment.get("word", "")
            segment["flagged"] = profanity.contains_profanity(word_text)
        return word_segments


ac = AudioCensor()
words = ac.transcribe_audio("./sample.wav")


print_json(data=ac.detect_profanity(words))
