# -*- coding: utf-8 -*-
from typing import Callable

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from src.logging import logger
from src.config import settings


def setup_auth_middleware(app: FastAPI) -> None:
    if settings.AUTH_ENABLED:
        app.add_middleware(AuthMiddleware)
    else:
        logger.warn(
            "Authentication has been disabled. Make sure this is intended.",
            auth_enabled=settings.AUTH_ENABLED,
        )


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content="Unauthorized")
        token = auth_header[len("Bearer ") :].strip()
        if "*" not in settings.AUTH_TOKENS and token not in settings.AUTH_TOKENS:
            return JSONResponse(status_code=401, content="Unauthorized")
        return await call_next(request)
