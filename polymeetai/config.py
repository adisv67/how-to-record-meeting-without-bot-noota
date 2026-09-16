from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    sample_rate: int = 16000
    block_size: int = 512
    channels: int = 1
    input_device: int | None = None

    # Made more sensitive for testing
    vad_threshold: float = 0.3
    min_speech_duration: float = 0.25
    min_silence_duration: float = 0.3
    speech_pad_ms: int = 200

    # Changed to use the C++ model path
    whisper_model: str = "models/ggml-small.bin"
    whisper_task: str = "translate"
    language: str | None = None

    overlay_lines: int = 3
    overlay_width: int = 900
    overlay_bottom_margin: int = 120

    db_path: str = "polymeetai.db"
