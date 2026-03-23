import uuid

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class AppError(HTTPException):
    def __init__(self, status_code: int, code: str, message: str, details: list | None = None):
        self.code = code
        self.error_message = message
        self.details = details or []
        super().__init__(status_code=status_code, detail=message)


ERROR_CODES = {
    400: "VALIDATION_ERROR",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    429: "RATE_LIMITED",
    500: "INTERNAL_ERROR",
}


async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.error_message,
                "details": exc.details,
                "request_id": str(uuid.uuid4()),
            }
        },
    )


async def generic_error_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    code = ERROR_CODES.get(exc.status_code, "INTERNAL_ERROR")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": code,
                "message": str(exc.detail),
                "details": [],
                "request_id": str(uuid.uuid4()),
            }
        },
    )
