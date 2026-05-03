import os
from pydantic import BaseModel, Field
from PIL import ImageGrab, Image
from typing import Dict, Any

from ..tools.base import AsyncTool, RiskLevel
from ..tools.registry import tool_registry
from ..vision.service import vision_service
from ..vision.annotator import annotate_image
from ...core.logging import logger

class TakeScreenshotParams(BaseModel):
    save_path: str = Field(description="The path to save the screenshot locally (e.g., /tmp/screenshot.png)")

class TakeScreenshotTool(AsyncTool):
    name = "take_screenshot"
    description = "Captures the current desktop screen and saves it as an image file."
    risk_level = RiskLevel.LOW
    schema = TakeScreenshotParams

    async def execute(self, params: Dict[str, Any]) -> str:
        save_path = params.get("save_path")
        
        try:
            # Capture the entire screen
            screenshot = ImageGrab.grab()
            screenshot.save(save_path)
            return f"Screenshot successfully saved to {save_path}"
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}", exc_info=True)
            return f"Error capturing screenshot: {str(e)}"

class LocateUIElementParams(BaseModel):
    image_path: str = Field(description="The path to the screenshot image to analyze")
    description: str = Field(description="Description of the UI element to locate (e.g., 'Submit button', 'Search bar')")
    annotate_output_path: str = Field(default="", description="Optional path to save a copy of the image with a bounding box drawn over the found element")

class LocateUIElementTool(AsyncTool):
    name = "locate_ui_element"
    description = "Uses AI vision to find a specific UI element in a screenshot and returns its bounding box coordinates."
    risk_level = RiskLevel.LOW
    schema = LocateUIElementParams

    async def execute(self, params: Dict[str, Any]) -> str:
        image_path = params.get("image_path")
        description = params.get("description")
        annotate_output_path = params.get("annotate_output_path")

        if not os.path.exists(image_path):
            return f"Error: Image file not found at {image_path}"

        try:
            image = Image.open(image_path)
            
            # Use Vision Service to locate element
            coords = vision_service.locate_element(image, description)
            
            if not coords:
                return f"Could not locate element matching '{description}'"
                
            # Optionally annotate and save
            if annotate_output_path:
                annotated = annotate_image(image, coords, label=description)
                annotated.save(annotate_output_path)
                return f"Element found at {coords}. Annotated image saved to {annotate_output_path}"
                
            return f"Element found at {coords}."
            
        except Exception as e:
            logger.error(f"Error in UI element location tool: {e}")
            return f"Error analyzing image: {str(e)}"

# Self-registration logic
def register_tools(registry):
    registry.register(TakeScreenshotTool())
    registry.register(LocateUIElementTool())

# Execute immediately for global registry if imported
register_tools(tool_registry)
