import threading
import time
from loguru import logger
import litellm

class IntelligenceWorker:
    def __init__(self, get_transcript_callback, update_notes_callback):
        self.get_transcript = get_transcript_callback
        self.update_notes = update_notes_callback
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self):
        # Wait 5 minutes (300 seconds) before the first run
        if self._stop.wait(300):
            return

        while not self._stop.is_set():
            logger.info("Intelligence Worker: Generating meeting notes...")
            transcript = self.get_transcript()
            
            # If there hasn't been much talking, wait another 5 mins
            if len(transcript.split()) < 20:
                logger.info("Not enough text to summarize yet. Waiting another 5 mins.")
                if self._stop.wait(300): return
                continue

            prompt = f"""You are an AI meeting assistant. Analyze the following live meeting transcript and extract:
            1. 📝 **Summary** (2 bullet points of the main topics)
            2. ✅ **Action Items** (e.g., "- Adesh -> review SEO")
            3. 🎯 **Decisions** (e.g., "- Launch delayed")
            
            Format as clean Markdown. Be concise.
            
            Transcript:
            {transcript}
            """

            try:
                # Call local Ollama model
                response = litellm.completion(
                    model="ollama/qwen2.5:3b",
                    messages=[{"role": "user", "content": prompt}],
                    api_base="http://localhost:11434"
                )
                notes = response.choices[0].message.content
                self.update_notes(notes)
                logger.success("Meeting notes updated.")
            except Exception as e:
                logger.error(f"Ollama LLM failed: {e}")

            # Wait 5 minutes (300 seconds) for the next run
            if self._stop.wait(300):
                break

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop.set()
