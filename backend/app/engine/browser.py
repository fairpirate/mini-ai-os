import asyncio
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import Optional
from ..core.logging import logger

class BrowserEngine:
    """Manages a persistent Playwright browser session for JARVIS."""
    def __init__(self):
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._lock = asyncio.Lock()

    async def start(self):
        """Initializes the browser and persistent context."""
        logger.info("Initializing Browser Automation Engine...")
        try:
            self._playwright = await async_playwright().start()
            # Launch in headless mode for server execution, but could be headful for local dev
            self._browser = await self._playwright.chromium.launch(headless=True)
            self._context = await self._browser.new_context(
                viewport={'width': 1280, 'height': 800},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            self._page = await self._context.new_page()
            logger.info("Browser Engine running successfully.")
        except Exception as e:
            logger.error(f"Failed to start Browser Engine: {e}")

    async def stop(self):
        """Gracefully closes the browser."""
        logger.info("Shutting down Browser Automation Engine...")
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def get_page(self) -> Optional[Page]:
        """Returns the active page."""
        if not self._page:
            logger.warning("Browser Engine requested page but it is not initialized.")
            return None
        return self._page

browser_engine = BrowserEngine()
