import time
from fastapi import Request
from loguru import logger


async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        f"Response: {response.status_code} - Process Time: {process_time:.4f}s"
    )
    return response
