from pathlib import Path
from typing import NotRequired, TypedDict

import whisperx
from better_profanity import profanity
from pydub import AudioSegment
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
        audio = whisperx.load_audio(audio_path)

        result = self.model.transcribe(audio, batch_size=16, language=self.language)

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

    def mute_audio(
        self,
        input_path: str,
        output_path: str,
        word_segments: list[Word],
        beep: bool = False,
    ) -> None:
        """
        Loops over the word segments and mutes or beeps the audio where a word is flagged.
        Saves the updated audio at the output_path using pydub.
        """
        from pydub.generators import Sine

        audio = AudioSegment.from_file(input_path)

        for segment in word_segments:
            if segment.get("flagged", False):
                start_ms = int(segment.get("start", 0) * 1000)
                end_ms = int(segment.get("end", 0) * 1000)

                # Ensure the time bounds are valid within the audio duration
                start_ms = max(0, start_ms)
                end_ms = min(len(audio), end_ms)

                if start_ms < end_ms:
                    duration = end_ms - start_ms
                    if beep:
                        # Generate a 1000 Hz sine wave beep with matching duration
                        replacement = (
                            Sine(1000)
                            .to_audio_segment(duration=duration)
                            .apply_gain(-3)
                        )
                    else:
                        replacement = AudioSegment.silent(duration=duration)
                    audio = audio[:start_ms] + replacement + audio[end_ms:]

        output_format = Path(output_path).suffix.lstrip(".").lower() or "wav"
        audio.export(output_path, format=output_format)


ac = AudioCensor()
words = ac.transcribe_audio("./sample.wav")

ac.mute_audio(
    input_path="./sample.wav",
    output_path="./sample-censored.wav",
    word_segments=ac.detect_profanity(words),
)


print_json(data=ac.detect_profanity(words))
