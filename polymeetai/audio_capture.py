import sounddevice as sd
import numpy as np
import threading
from .config import Config

def find_blackhole() -> int | None:
    for i, name in enumerate(sd.query_devices()):
        if "BlackHole" in name["name"] and name["max_input_channels"] >= 1:
            return i
    return None

class AudioCapture:
    def __init__(self, cfg: Config, on_frame):
        self.cfg = cfg
        self.on_frame = on_frame
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._t = 0.0

    def _callback(self, indata, frames, time_info, status):
        mono = indata[:, 0].copy()
        self._t += frames / self.cfg.sample_rate
        self.on_frame(mono, self._t)

    def start(self):
        dev = self.cfg.input_device or find_blackhole()
        if dev is None:
            raise RuntimeError("BlackHole not found. Install it and create a Multi-Output Device.")
        self._thread = threading.Thread(target=self._run, args=(dev,), daemon=True)
        self._thread.start()

    def _run(self, dev):
        with sd.InputStream(
            device=dev,
            samplerate=self.cfg.sample_rate,
            channels=self.cfg.channels,
            blocksize=self.cfg.block_size,
            dtype="float32",
            callback=self._callback,
        ):
            self._stop.wait()

    def stop(self):
        self._stop.set()
