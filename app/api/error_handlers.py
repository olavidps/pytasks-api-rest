"""Exception handlers for the API."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.exceptions.user import UserAlreadyExistsError, UserNotFoundError


class AppException(Exception):
    """Base exception for application errors."""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


def register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers for the FastAPI application."""

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(UserNotFoundError)
    async def user_not_found_handler(
        request: Request, exc: UserNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)},
        )

    @app.exception_handler(UserAlreadyExistsError)
    async def user_already_exists_handler(
        request: Request, exc: UserAlreadyExistsError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"detail": str(exc)},
        )
