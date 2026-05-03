from typing import Dict, Any
from PIL import Image, ImageDraw

def annotate_image(image: Image.Image, coords: Dict[str, float], label: str = "") -> Image.Image:
    """
    Draws a red bounding box and an optional label on the image.
    coords should have normalized x1, y1, x2, y2 (0.0 to 1.0).
    Returns a new Image object.
    """
    if not all(k in coords for k in ("x1", "y1", "x2", "y2")):
        return image
        
    width, height = image.size
    
    # Convert normalized coordinates to absolute pixels
    x1 = int(coords["x1"] * width)
    y1 = int(coords["y1"] * height)
    x2 = int(coords["x2"] * width)
    y2 = int(coords["y2"] * height)
    
    # Create a copy so we don't modify the original
    annotated = image.copy()
    draw = ImageDraw.Draw(annotated)
    
    # Draw red rectangle with a thickness of 3 pixels
    draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
    
    if label:
        # Draw a small background for text readability
        draw.rectangle([x1, max(0, y1-15), x1+len(label)*6, y1], fill="red")
        draw.text((x1+2, max(0, y1-15)), label, fill="white")
        
    return annotated
