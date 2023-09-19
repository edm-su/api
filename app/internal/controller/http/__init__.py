import logging.config

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app import __version__
from app.internal.controller.http.router import api_router
from app.internal.entity.settings import settings
from app.pkg.meilisearch import config_ms, ms_client

openapi_url = None if settings.disable_openapi else "/openapi.json"
app = FastAPI(
    openapi_url=openapi_url,
    debug=False,
    version=__version__,
)


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


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["x-total-count"],
)
