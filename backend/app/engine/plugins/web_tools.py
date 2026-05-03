import webbrowser
from pydantic import BaseModel, Field
from typing import Dict, Any
from ..tools.base import AsyncTool, RiskLevel

class OpenWebsiteSchema(BaseModel):
    url: str = Field(..., description="The complete URL to open (must include http/https).")

class OpenWebsiteTool(AsyncTool):
    name = "open_website"
    description = "Opens a website URL in the default browser."
    risk_level = RiskLevel.LOW
    schema = OpenWebsiteSchema

    async def execute(self, params: Dict[str, Any]) -> str:
        url = params["url"]
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
            
        try:
            success = webbrowser.open(url)
            if success:
                return f"Opened website: {url}"
            return "Failed to open website."
        except Exception as e:
            return f"Error opening website: {e}"

def register_tools(registry):
    registry.register(OpenWebsiteTool())
