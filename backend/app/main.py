from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Core imports
from .core.config import settings
from .core.logging import logger
from .core.exceptions import global_exception_handler
from .core.middleware import log_requests_middleware
from .engine.queue import task_manager
from .engine.tools.registry import tool_registry
from .engine.browser import browser_engine
from .engine.plugins.manager import plugin_manager

# Routers
from .api.routers import system, ws, legacy

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize background services
    logger.info("Initializing MEGAN Background Systems...")
    await task_manager.start()
    tool_registry.load_plugins()
    await plugin_manager.discover()
    logger.info("Plugin Registry and Manager Loaded.")
    await browser_engine.start()
    
    yield
    
    # Shutdown: Clean up resources
    logger.info("Shutting down MEGAN systems...")
    await browser_engine.stop()
    await task_manager.stop()

def create_app() -> FastAPI:
    """Factory function to configure and return the FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        lifespan=lifespan
    )

    # Middleware setup
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Custom Middlewares
    app.middleware("http")(log_requests_middleware)
    
    # Exception Handlers
    app.add_exception_handler(Exception, global_exception_handler)

    # Include modular routers
    app.include_router(system.router, prefix=settings.API_V1_STR + "/system", tags=["System"])
    app.include_router(ws.router, prefix="/ws", tags=["WebSocket"])
    app.include_router(legacy.router, tags=["Legacy"])

    return app

app = create_app()

@app.get("/")
async def root():
    return {"message": f"{settings.PROJECT_NAME} API v{settings.VERSION} is running."}
