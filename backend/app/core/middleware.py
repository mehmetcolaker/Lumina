"""Centralised middleware and exception handlers for the Lumina API.

Registers CORS and a global JSON exception handler that catches all
unhandled ``Exception`` instances and returns a structured 500 response
instead of an HTML error page.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def register_middleware(app: FastAPI) -> None:
    """Attach CORS middleware and global exception handlers to the app.

    Should be called once during application construction in ``main.py``.

    Args:
        app: The FastAPI application instance.
    """

    # ---- CORS ----
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---- Global 500 handler ----
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Catch all unhandled exceptions and return a JSON 500."""
        logger.exception("Unhandled exception on %s %s", request.method, request.url)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An internal server error occurred.",
                "error_type": type(exc).__name__,
            },
        )
