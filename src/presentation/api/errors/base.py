# app/core/decorators.py
import logging
from typing import Type

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from infrastructure.exceptions import (
    DatabaseConnectionException,
    EntityNotFoundException,
    EntityAlreadyExistsException,
    FieldException,
    PageNotFoundException
)

_log = logging.getLogger(__name__)


class ErrorsHandler:

    def __init__(self, app: FastAPI):

        self.errors: dict[Type[Exception], int] = {
            DatabaseConnectionException: 500,
            EntityNotFoundException: 404,
            EntityAlreadyExistsException: 409,
            FieldException: 400,
            PageNotFoundException: 404
        }

        for error in self.errors:
            app.add_exception_handler(
                error, self.create_handler(self.errors[error]))

    def create_handler(self, status_code: int):
        async def handler(request: Request, exc: Exception):
            return JSONResponse(
                status_code=status_code,
                content={"detail": str(exc)},
            )

        return handler
