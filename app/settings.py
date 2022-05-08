from typing import TYPE_CHECKING

from pydantic import BaseSettings

if TYPE_CHECKING:
    PostgresDsn = str
else:
    from pydantic import PostgresDsn


class Settings(BaseSettings):
    email_from: str = 'noreply@edm.su'
    secret_key: str
    static_url: str = 'https://static.dev.edm.su'
    database_url: PostgresDsn = 'postgresql://postgres:postgres@db/postgres'
    frontend_url: str = 'https://edm.su'
    debug: bool = False
    testing: bool = False

    meilisearch_api_url: str = 'http://localhost:7700'
    meilisearch_api_key: str = ''
    meilisearch_index_postfix: str = ''

    s3_bucket: str
    s3_endpoint: str
    s3_access_key: str
    s3_access_key_id: str

    smtp_server: str
    smtp_port: int
    smtp_user: str
    smtp_password: str


settings = Settings()
