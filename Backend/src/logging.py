# -*- coding: utf-8 -*-
import logging as log

import structlog
from structlog.stdlib import BoundLogger

from src.config import settings

logger: BoundLogger = structlog.get_logger()
logger.info(
    "logging_initialized",
    environment=settings.ENVIRONMENT.value,
    log_level=settings.LOG_LEVEL,
    log_format=settings.LOG_FORMAT,
)
log.getLogger("httpx").setLevel(log.WARNING)
