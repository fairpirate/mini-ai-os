import io
try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    
from ...core.logging import logger

class STTEngine:
    """Speech-to-Text Engine using faster-whisper."""
    def __init__(self, model_size="tiny.en", device="cpu", compute_type="int8"):
        if not WHISPER_AVAILABLE:
            logger.warning("faster-whisper is not installed. STT will be disabled.")
            self.model = None
            return

        logger.info(f"Loading Whisper model '{model_size}'...")
        try:
            self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
            logger.info("Whisper model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            self.model = None

    async def transcribe(self, audio_data: bytes) -> str:
        """Transcribe binary audio data (WAV/PCM) to text."""
        if not self.model:
            return ""
            
        try:
            # faster-whisper can read from a file-like object
            audio_io = io.BytesIO(audio_data)
            segments, info = self.model.transcribe(audio_io, beam_size=5, vad_filter=True)
            
            transcript = " ".join([segment.text for segment in segments]).strip()
            return transcript
        except Exception as e:
            logger.error(f"Transcription error: {e}", exc_info=True)
            return ""

stt_engine = STTEngine()
