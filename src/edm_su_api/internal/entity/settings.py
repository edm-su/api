from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class DBSettings(BaseSettings):
    database_url: PostgresDsn


class Settings(DBSettings):
    log_level: str = "ERROR"
    disable_openapi: bool = False
    static_url: str = "https://static.dev.edm.su"

    host: str = "127.0.0.1"
    port: int = 8000

    spicedb_url: str
    spicedb_api_key: str
    spicedb_insecure: bool = False
    spicedb_tls_cert: str | None = None

    s3_bucket: str
    s3_endpoint: str
    s3_access_key: str
    s3_access_key_id: str
    s3_region: str = "us-east-1"


settings = Settings.model_validate({})
db_settings = Settings.model_validate({})
