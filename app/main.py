import logging.config

import uvicorn
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from starlette import status
from starlette.middleware.cors import CORSMiddleware

from app.internal.controller.http.router import api_router
from app.internal.usecase.exceptions.user import AuthError, UserError
from app.meilisearch import config_ms, ms_client
from app.settings import settings

openapi_url = None if settings.disable_openapi else "/openapi.json"
app = FastAPI(openapi_url=openapi_url, debug=False)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default_formatter": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "stream_handler": {
            "class": "logging.StreamHandler",
            "formatter": "default_formatter",
        },
    },
    "loggers": {
        "app": {
            "handlers": ["stream_handler"],
            "level": settings.log_level,
            "propagate": True,
        },
        "sqlalchemy.engine": {
            "handlers": ["stream_handler"],
            "level": settings.log_level,
            "propagate": True,
        },
    },
}
logging.config.dictConfig(LOGGING_CONFIG)


@app.on_event("startup")
async def startup() -> None:
    await config_ms(ms_client)


@app.on_event("shutdown")
async def shutdown() -> None:
    await ms_client.aclose()


origins = ["https://edm.su", "http://localhost:3000"]

app.include_router(api_router)


@app.exception_handler(AuthError)
async def auth_exception_handler(
    response: Response,
    exc: AuthError,
) -> JSONResponse:
    response.headers["WWW-Authenticate"] = "Bearer"
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"error": "invalid_token", "error_description": str(exc)},
    )


@app.exception_handler(UserError)
async def user_exception_handler(exc: UserError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"error": "invalid_client", "error_description": str(exc)},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["x-total-count"],
)

if __name__ == "__main__":
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"][
        "fmt"
    ] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_config["formatters"]["default"][
        "fmt"
    ] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    uvicorn.run(
        "app.main:app",
        log_config=log_config,
        log_level=settings.log_level.lower(),
        reload=True,
    )
