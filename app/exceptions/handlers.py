from fastapi import Request, status
from fastapi.responses import JSONResponse
from loguru import logger

from .exceptions import NotFoundException, ValidationException


async def not_found_exception_handler(request: Request, exc: NotFoundException):
    logger.warning(f"NotFoundException: {exc} for request {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": str(exc)},
    )


async def validation_exception_handler(request: Request, exc: ValidationException):
    logger.warning(f"ValidationException: {exc} for request {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": str(exc)},
    )


def setup_exception_handlers(app):
    app.add_exception_handler(NotFoundException, not_found_exception_handler)
    app.add_exception_handler(ValidationException, validation_exception_handler)
