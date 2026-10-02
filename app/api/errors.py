from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)


templates = Jinja2Templates(directory="templates")


def register_exception_handlers(app):

    @app.exception_handler(StarletteHTTPException)
    async def general_http_exception_handler(
        request: Request,
        exception: StarletteHTTPException,
    ):
        if request.url.path.startswith("/api"):
            return await http_exception_handler(request, exception)

        message = (
                    exception.detail
                    if exception.detail
                    else "An error occurred. Please check your request and try again."
                )
        

        return templates.TemplateResponse(
            request,
            "error.html",
            {
                "status_code": exception.status_code,
                "title": exception.status_code,
                "message": message,
            },
            status_code=exception.status_code,
        )


    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exception: RequestValidationError,
    ):

        if request.url.path.startswith("/api"):
            return await request_validation_exception_handler(request, exception)

        return templates.TemplateResponse(
            request,
            "error.html",
            {
                "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
                "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
                "message": "Invalid request. Please check your input and try again.",
            },
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )