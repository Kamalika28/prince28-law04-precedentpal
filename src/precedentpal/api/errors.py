"""RFC 9457-style problem responses for API errors."""

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        title = "Not Found" if exc.status_code == 404 else "HTTP Error"
        body: dict[str, Any] = {
            "type": "about:blank",
            "title": title,
            "status": exc.status_code,
            "detail": str(exc.detail),
            "instance": request.url.path,
            "request_id": request_id,
        }
        return JSONResponse(
            body,
            status_code=exc.status_code,
            media_type="application/problem+json",
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        errors = [
            {
                "field": ".".join(str(part) for part in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
            for error in exc.errors()
        ]
        body = {
            "type": "about:blank",
            "title": "Unprocessable Content",
            "status": 422,
            "detail": "The request contains invalid input.",
            "instance": request.url.path,
            "request_id": request_id,
            "errors": errors,
        }
        return JSONResponse(
            body, status_code=422, media_type="application/problem+json"
        )
