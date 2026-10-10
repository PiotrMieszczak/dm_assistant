from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.shared import DomainError, NotFound, ValidationFailed


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFound)
    async def not_found(_request: Request, exc: NotFound) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ValidationFailed)
    async def invalid(_request: Request, exc: ValidationFailed) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(DomainError)
    async def domain(_request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})
