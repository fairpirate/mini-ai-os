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

class SearchWebSchema(BaseModel):
    query: str = Field(..., description="The search query.")

class SearchWebTool(AsyncTool):
    name = "search_web"
    description = "Searches the web for information (Mocked)."
    risk_level = RiskLevel.LOW
    schema = SearchWebSchema

    async def execute(self, params: Dict[str, Any]) -> str:
        query = params["query"]
        return f"Top search results for '{query}':\n1. Wikipedia: Information about {query}\n2. News: Latest updates on {query}\n3. Official Website for {query}"

class GetWeatherSchema(BaseModel):
    location: str = Field(..., description="The location to get weather for.")

class GetWeatherTool(AsyncTool):
    name = "get_weather"
    description = "Gets the current weather for a location (Mocked)."
    risk_level = RiskLevel.LOW
    schema = GetWeatherSchema

    async def execute(self, params: Dict[str, Any]) -> str:
        location = params["location"]
        return f"The current weather in {location} is 72°F (22°C) with clear skies."

class DeployAppSchema(BaseModel):
    pass

class DeployAppTool(AsyncTool):
    name = "deploy_app"
    description = "Deploys the application to a cloud provider (Stub)."
    risk_level = RiskLevel.HIGH
    schema = DeployAppSchema

    async def execute(self, params: Dict[str, Any]) -> str:
        return "Deployment initiated (Mock). Application will be live at: https://demo-app.example.com"

class PostInstagramSchema(BaseModel):
    caption: str = Field(..., description="The caption for the post.")
    image_url: str = Field("", description="Optional image URL.")

class PostInstagramTool(AsyncTool):
    name = "post_instagram"
    description = "Posts a caption and image to Instagram (Stub)."
    risk_level = RiskLevel.MEDIUM
    schema = PostInstagramSchema

    async def execute(self, params: Dict[str, Any]) -> str:
        return f"Successfully posted to Instagram: '{params.get('caption')}'"

def register_tools(registry):
    registry.register(OpenWebsiteTool())
    registry.register(SearchWebTool())
    registry.register(GetWeatherTool())
    registry.register(DeployAppTool())
    registry.register(PostInstagramTool())
