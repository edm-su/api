from typing import TYPE_CHECKING

from pydantic import BaseSettings

if TYPE_CHECKING:
    PostgresDsn = str
else:
    from pydantic import PostgresDsn


class Settings(BaseSettings):
    email_from: str = 'noreply@edm.su'
    secret_key: str = 'bhdasbdashjcxjhzbjhdasjhdasdbasj'
    static_url: str = 'https://static.dev.edm.su'
    database_url: PostgresDsn = 'postgresql://postgres:postgres@db/postgres'
    frontend_url: str = 'https://edm.su'
    debug: bool = False
    testing: bool = False
    # Algolia settings
    algolia_app_id: str
    algolia_api_key: str
    algolia_index: str
    # S3 bucket settings
    s3_bucket: str
    s3_endpoint: str
    s3_access_key: str
    s3_access_key_id: str
    # SMTP settings
    smtp_server: str
    smtp_port: int
    smtp_user: str
    smtp_password: str


settings = Settings()
