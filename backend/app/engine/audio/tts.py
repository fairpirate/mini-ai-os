import os
import subprocess
import asyncio
from ...core.logging import logger

class TTSEngine:
    """
    Text-to-Speech Engine.
    Uses macOS native 'say' command as a high-performance fallback for immediate execution,
    with an interface prepared for Piper TTS ONNX models.
    """
    def __init__(self, use_mac_native=True):
        self.use_mac_native = use_mac_native
        logger.info("TTS Engine initialized.")

    async def synthesize_stream(self, text: str):
        """
        Synthesizes text into audio bytes and yields them.
        For macOS native fallback, it speaks immediately but we return empty bytes to satisfy the stream interface.
        """
        if not text.strip():
            return
            
        try:
            if self.use_mac_native and os.uname().sysname == "Darwin":
                # Use macOS built-in TTS (very low latency)
                # Run asynchronously so it doesn't block the event loop
                process = await asyncio.create_subprocess_exec(
                    "say", text,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL
                )
                await process.communicate()
                yield b"" # Yield empty bytes since audio plays directly on the host
            else:
                # Piper TTS implementation placeholder
                # In production, this would load the ONNX model and yield PCM audio chunks
                # piper_tts.synthesize(text, model, callback=yield_chunk)
                logger.warning("Piper TTS ONNX model loading not implemented. Skipping TTS.")
                yield b""
        except Exception as e:
            logger.error(f"TTS Synthesis error: {e}", exc_info=True)

tts_engine = TTSEngine()
