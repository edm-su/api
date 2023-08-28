from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    log_level: str = "ERROR"
    disable_openapi: bool = False
    static_url: str = "https://static.dev.edm.su"
    database_url: PostgresDsn

    host: str = "127.0.0.1"
    port: int = 8000

    meilisearch_api_url: str = "http://localhost:7700"
    meilisearch_api_key: str = ""
    meilisearch_index_postfix: str = ""

    spicedb_url: str
    spicedb_api_key: str

    s3_bucket: str
    s3_endpoint: str
    s3_access_key: str
    s3_access_key_id: str
    s3_region: str = "us-east-1"


settings = Settings.model_validate({})
