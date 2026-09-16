import sys
import time
import queue
import threading
import signal
import numpy as np
from loguru import logger

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from .config import Config
from .audio_capture import AudioCapture
from .vad import VadSegmenter
from .transcriber import Transcriber
from .overlay import SubtitleWindow, SubtitleBridge
from .db import init_db, start_meeting, end_meeting, insert_segment

def main():
    cfg = Config()
    logger.info("PolyMeetAI starting (Sprint 1B - Scrollable Subtitles)")

    conn = init_db(cfg.db_path)
    meeting_id = start_meeting(conn, title="Google Meet")
    t0 = time.monotonic()

    app = QApplication(sys.argv)
    
    # Fix for Control + C in Terminal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(500)

    overlay = SubtitleWindow(cfg)
    bridge = SubtitleBridge()
    bridge.new_text.connect(overlay.push_text)
    overlay.show()

    transcriber = Transcriber(cfg)
    segment_q: "queue.Queue[tuple[np.ndarray, float, float]]" = queue.Queue()

    def whisper_worker():
        while True:
            seg = segment_q.get()
            if seg is None:
                break
            audio, ts_start, ts_end = seg
            try:
                english, src_lang = transcriber.translate(audio)
                if english:
                    logger.success(f"-> {english}")
                    bridge.new_text.emit(english)
                    insert_segment(conn, meeting_id, ts_start, ts_end, src_lang, None, english)
                del audio
            except Exception as e:
                logger.exception(f"transcription failed: {e}")

    worker = threading.Thread(target=whisper_worker, daemon=True)
    worker.start()

    vad = VadSegmenter(cfg)
    vad.start_clock(t0)

    def on_frame(frame, frame_t):
        seg = vad.push(frame, frame_t)
        if seg is not None:
            audio, ts_start, ts_end = seg
            segment_q.put((audio, ts_start, ts_end))

    capture = AudioCapture(cfg, on_frame=on_frame)
    capture.start()
    logger.info("Capturing from BlackHole. Scrollable Subtitle Mode active.")

    try:
        app.exec()
    finally:
        capture.stop()
        segment_q.put(None)
        worker.join(timeout=2)
        end_meeting(conn, meeting_id)
        conn.close()
        logger.info("PolyMeetAI stopped.")

if __name__ == "__main__":
    from polymeetai.main import main
    main()
