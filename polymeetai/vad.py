from collections import deque
import numpy as np
from silero_vad import VADIterator, load_silero_vad
from .config import Config

class VadSegmenter:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.model = load_silero_vad()
        self.iterator = VADIterator(
            self.model,
            threshold=cfg.vad_threshold,
            min_silence_duration_ms=int(cfg.min_silence_duration * 1000),
            speech_pad_ms=cfg.speech_pad_ms,
        )
        self._buffer: list[np.ndarray] = []
        self._speech_start: float | None = None
        self._t0 = None

    def start_clock(self, t0: float):
        self._t0 = t0

    def push(self, frame: np.ndarray, frame_t: float) -> tuple[np.ndarray, float, float] | None:
        self._buffer.append(frame)
        speech_dict = self.iterator(frame.astype(np.float32), return_seconds=False)
        if speech_dict:
            if "start" in speech_dict and self._speech_start is None:
                self._speech_start = max(0.0, frame_t - 0.2)
            if "end" in speech_dict and self._speech_start is not None:
                audio = np.concatenate(self._buffer)
                ts_start, ts_end = self._speech_start, frame_t
                self._buffer.clear()
                self._speech_start = None
                self.iterator.reset_states()
                return audio, ts_start, ts_end
        return None
