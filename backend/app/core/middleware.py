import time
from fastapi import Request
from .logging import logger

async def log_requests_middleware(request: Request, call_next):
    """Middleware to log request processing time and paths."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Path: {request.url.path} - Method: {request.method} - Time: {process_time:.4f}s")
    return response
