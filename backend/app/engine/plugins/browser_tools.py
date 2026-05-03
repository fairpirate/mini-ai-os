import json
from pydantic import BaseModel, Field
from typing import Dict, Any
from ..tools.base import AsyncTool, RiskLevel
from ..browser import browser_engine
from ...core.logging import logger

class NavigateBrowserSchema(BaseModel):
    url: str = Field(..., description="The full URL to navigate to (e.g., https://example.com).")

class NavigateBrowserTool(AsyncTool):
    name = "navigate_browser"
    description = "Navigates the autonomous browser to a specific URL."
    risk_level = RiskLevel.LOW
    schema = NavigateBrowserSchema

    async def execute(self, params: Dict[str, Any]) -> str:
        page = await browser_engine.get_page()
        if not page:
            return "Error: Browser Engine is not active."
        url = params["url"]
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            return f"Successfully navigated to {url}. Title: {await page.title()}"
        except Exception as e:
            return f"Failed to navigate: {e}"

class ScrapePageSchema(BaseModel):
    pass # No params needed to scrape current page

class ScrapePageTool(AsyncTool):
    name = "scrape_page"
    description = "Scrapes the text content and interactive elements of the current browser page."
    risk_level = RiskLevel.LOW
    schema = ScrapePageSchema

    async def execute(self, params: Dict[str, Any]) -> str:
        page = await browser_engine.get_page()
        if not page:
            return "Error: Browser Engine is not active."
            
        try:
            # Extract basic text content and interactive elements
            # In a full implementation, this maps the DOM tree to interactive IDs
            text_content = await page.evaluate("() => document.body.innerText")
            links = await page.evaluate("() => Array.from(document.querySelectorAll('a')).slice(0, 10).map(a => ({text: a.innerText, href: a.href}))")
            
            summary = text_content[:1500] + "...\n\nLinks found:\n" + json.dumps(links, indent=2)
            return summary
        except Exception as e:
            return f"Failed to scrape page: {e}"

class ClickElementSchema(BaseModel):
    selector: str = Field(..., description="The CSS selector or text of the element to click.")

class ClickElementTool(AsyncTool):
    name = "click_element"
    description = "Clicks an element on the current browser page using a CSS selector or text."
    risk_level = RiskLevel.MEDIUM
    schema = ClickElementSchema

    async def execute(self, params: Dict[str, Any]) -> str:
        page = await browser_engine.get_page()
        if not page:
            return "Error: Browser Engine is not active."
            
        selector = params["selector"]
        try:
            # Try clicking by exact text first, then by selector
            try:
                await page.get_by_text(selector, exact=False).first.click(timeout=5000)
                return f"Successfully clicked element containing text '{selector}'."
            except:
                await page.click(selector, timeout=5000)
                return f"Successfully clicked element with selector '{selector}'."
        except Exception as e:
            return f"Failed to click element '{selector}': {e}"

class FillFormSchema(BaseModel):
    selector: str = Field(..., description="The CSS selector of the input field.")
    text: str = Field(..., description="The text to enter into the field.")

class FillFormTool(AsyncTool):
    name = "fill_form"
    description = "Fills an input field on the current browser page."
    risk_level = RiskLevel.MEDIUM
    schema = FillFormSchema

    async def execute(self, params: Dict[str, Any]) -> str:
        page = await browser_engine.get_page()
        if not page:
            return "Error: Browser Engine is not active."
            
        selector = params["selector"]
        text = params["text"]
        try:
            await page.fill(selector, text, timeout=5000)
            return f"Successfully filled '{selector}' with provided text."
        except Exception as e:
            return f"Failed to fill element '{selector}': {e}"


def register_tools(registry):
    registry.register(NavigateBrowserTool())
    registry.register(ScrapePageTool())
    registry.register(ClickElementTool())
    registry.register(FillFormTool())
