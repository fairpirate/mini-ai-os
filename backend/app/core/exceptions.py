from fastapi import Request
from fastapi.responses import JSONResponse
from .logging import logger

async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all for unhandled exceptions to prevent server crashes and notify HUD."""
    logger.error(f"Unhandled Exception: {exc}", exc_info=True)
    
    # Notify connected clients of the system fault
    from ..ws.manager import manager
    import asyncio
    asyncio.create_task(manager.broadcast({
        "event": "system_error",
        "payload": {"message": f"Critical Kernel Fault: {str(exc)}", "type": "unhandled_exception"}
    }))

    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error. The AI core experienced a fault."},
    )
