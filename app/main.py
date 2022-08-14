import logging.config

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.db import database
from app.internal.controller.http.router import api_router
from app.meilisearch import (
    ms_client,
    config_ms,
)
from app.routers import (
    comments,
    djs,
    livestreams,
    posts,
    tokens,
    upload,
    user_videos,
    users,
)
from app.settings import settings

openapi_url = None if settings.disable_openapi else "/openapi.json"
app = FastAPI(openapi_url=openapi_url, debug=False)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default_formatter": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
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
    await database.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    await database.disconnect()
    await ms_client.aclose()


origins = ["https://edm.su", "http://localhost:3000"]

app.include_router(user_videos.router)
app.include_router(tokens.router)
app.include_router(users.router)
app.include_router(comments.router)
app.include_router(posts.router)
app.include_router(upload.router)
app.include_router(livestreams.router)
app.include_router(djs.router)
app.include_router(tokens.router)
app.include_router(api_router)


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
