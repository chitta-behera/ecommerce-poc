import logging
import sys
from loguru import logger
from .config import settings


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging():
    # remove default handler
    logger.remove()
    # set new handler
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="{level} {message}",
    )
    # intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
