import base64
import json
import logging
from io import BytesIO
from typing import Dict, Any, Tuple
from PIL import Image

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

from ...core.config import settings
from ...core.logging import logger

class VisionService:
    def __init__(self):
        self.vision_model_name = settings.VISION_MODEL_NAME
        try:
            self.vision_model = ChatOllama(model=self.vision_model_name, temperature=0.1)
            self._vlm_available = True
        except Exception as e:
            logger.warning(f"Vision model '{self.vision_model_name}' unavailable: {e}. VLM features disabled.")
            self.vision_model = None
            self._vlm_available = False

    def _encode_image(self, image: Image.Image) -> str:
        """Compresses and base64 encodes a PIL Image."""
        # Convert to RGB if necessary (e.g. RGBA from screenshot)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
            
        # Resize to save context tokens if it's too large
        max_size = (1024, 1024)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        buffered = BytesIO()
        image.save(buffered, format="JPEG", quality=85)
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def extract_text(self, image: Image.Image) -> str:
        """
        Extract text using OCR if available, otherwise fallback to VLM.
        """
        if TESSERACT_AVAILABLE:
            logger.info("Using Tesseract for OCR text extraction.")
            try:
                return pytesseract.image_to_string(image)
            except Exception as e:
                logger.warning(f"Tesseract failed: {e}. Falling back to VLM.")

        if not self._vlm_available:
            return "[Vision model unavailable — run 'ollama pull llava' to enable OCR.]"

        # Fallback to VLM
        logger.info("Using VLM for text extraction.")
        base64_image = self._encode_image(image)
        msg = HumanMessage(
            content=[
                {"type": "text", "text": "Extract all text visible in this image. Only output the extracted text."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
            ]
        )
        response = self.vision_model.invoke([msg])
        return response.content

    def locate_element(self, image: Image.Image, description: str) -> Dict[str, Any]:
        """
        Asks the VLM to find an element and return bounding box coordinates.
        Returns a dictionary with normalized coordinates: {"x1": 0.1, "y1": 0.1, "x2": 0.2, "y2": 0.2}
        """
        if not self._vlm_available:
            logger.warning(f"VLM unavailable — cannot locate UI element '{description}'.")
            return {}

        base64_image = self._encode_image(image)
        prompt = f"Find the UI element matching this description: '{description}'. Return its bounding box coordinates as a JSON object with keys x1, y1, x2, y2 representing normalized coordinates between 0.0 and 1.0. Do not output any other text."
        
        msg = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
            ]
        )
        
        try:
            response = self.vision_model.invoke([msg])
            content = response.content.strip()
            
            # Basic json cleanup in case of markdown formatting
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].strip()
                
            coords = json.loads(content)
            return coords
        except Exception as e:
            logger.error(f"VLM failed to locate element '{description}': {e}")
            return {}

vision_service = VisionService()
