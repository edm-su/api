import uvicorn
import uvicorn.config

from app.internal.entity.settings import settings

log_config = uvicorn.config.LOGGING_CONFIG
log_config["formatters"]["access"]["fmt"] = (
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
log_config["formatters"]["default"]["fmt"] = (
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
uvicorn.run(
    "app.internal.controller.http:app",
    log_config=log_config,
    log_level=settings.log_level.lower(),
    host=settings.host,
    port=settings.port,
)
