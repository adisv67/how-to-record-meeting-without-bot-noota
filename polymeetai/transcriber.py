import numpy as np
from loguru import logger
from pywhispercpp.model import Model
from .config import Config

class Transcriber:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        logger.info("Loading pywhispercpp model (Metal-accelerated)...")
        # Load the model. pywhispercpp automatically uses Apple Metal on M-series chips!
        self.model = Model(cfg.whisper_model, n_threads=4)

    def translate(self, audio: np.ndarray) -> tuple[str, str | None]:
        """Returns (english_text, source_lang)"""
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)
            
        # pywhispercpp uses translate=True instead of task='translate'
        segments = self.model.transcribe(audio, translate=True)
        
        # Combine all segments into one string
        text = " ".join([seg.text for seg in segments]).strip()
        
        return text, None
