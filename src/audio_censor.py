import whisperx
from rich import print_json


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


ac = AudioCensor()
result = ac.transcribe_audio("./sample.wav")


print_json(data=result)
