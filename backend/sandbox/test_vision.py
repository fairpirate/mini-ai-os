import asyncio
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.engine.plugins.vision_tools import TakeScreenshotTool, LocateUIElementTool

async def main():
    print("Testing Vision Analysis Pipeline...")
    
    screenshot_path = os.path.join(os.path.dirname(__file__), "test_screenshot.png")
    annotated_path = os.path.join(os.path.dirname(__file__), "test_annotated.png")
    
    # 1. Take a screenshot
    print(f"1. Taking screenshot to {screenshot_path}")
    screenshot_tool = TakeScreenshotTool()
    result = await screenshot_tool.execute({"save_path": screenshot_path})
    print(f"Screenshot Result: {result}")
    
    if not os.path.exists(screenshot_path):
        print("Failed to capture screenshot. Creating a synthetic image for testing.")
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (800, 600), color=(73, 109, 137))
        d = ImageDraw.Draw(img)
        d.text((100, 100), "Any prominent button or text element", fill=(255, 255, 0))
        img.save(screenshot_path)
        
    # 2. Try to locate an element (e.g. "File" menu or a generic item)
    print("2. Locating a UI element in the screenshot...")
    locator_tool = LocateUIElementTool()
    result = await locator_tool.execute({
        "image_path": screenshot_path,
        "description": "Any prominent button or text element",
        "annotate_output_path": annotated_path
    })
    print(f"Locator Result: {result}")
    
    if os.path.exists(annotated_path):
        print(f"Successfully generated annotated image at {annotated_path}")

if __name__ == "__main__":
    asyncio.run(main())
