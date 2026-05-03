import httpx
from typing import Dict, Any
from app.engine.plugins.sdk import JARVISPlugin, PluginTool
from app.engine.tools.base import RiskLevel
from pydantic import BaseModel, Field

class WeatherParams(BaseModel):
    location: str = Field(description="The city name to get weather for")

class Plugin(JARVISPlugin):
    async def initialize(self):
        """Register the weather tool on initialization."""
        weather_tool = PluginTool(
            name="get_weather_analytics",
            description="Fetches detailed atmospheric and weather data for a specific location.",
            risk=RiskLevel.LOW,
            schema=WeatherParams,
            func=self.get_weather
        )
        self.register_tool(weather_tool)
        print(f"Weather Plugin: Initialized and tool registered.")

    async def get_weather(self, params: Dict[str, Any]) -> str:
        location = params.get("location")
        # In a real plugin, we would use settings['api_key']
        # For now, we mock the response
        return f"Weather in {location}: 22°C, Clear Sky. Wind: 5km/h. Humidity: 45%."

    @JARVISPlugin.on("user_message")
    async def on_user_message(self, payload: Any):
        print(f"Weather Plugin: Observed user message -> {payload.get('text', '')[:20]}...")
