from os import getenv

EMAIL_FROM = getenv('EMAIL_FROM', 'noreply@edm.su')

SECRET_KEY = getenv('SECRET_KEY', 'bhdasbdashjcxjhzbjhdasjhdasdbasj')

STATIC_URL = getenv('STATIC_URL', 'https://static.dev.edm.su')

DATABASE_URL = getenv('DATABASE_URL', 'postgresql://postgres:postgres@db/postgres')

REDIS_URL = getenv('REDIS_URL', 'redis://redis:6379')

FRONTEND_URL = getenv('FRONTEND_URL', 'https://edm.su')

SENDGRID_API_KEY = getenv('SENDGRID_API_KEY')

YOUTUBE_API_KEY = getenv('YOUTUBE_API_KEY')

TEST = getenv('TEST', False)

ALGOLIA_APP_ID = getenv('ALGOLIA_APP_ID')
ALGOLIA_API_KEY = getenv('ALGOLIA_API_KEY')
ALGOLIA_INDEX = getenv('ALGOLIA_INDEX')

S3_BUCKET = getenv('S3_BUCKET')
S3_ENDPOINT = getenv('S3_ENDPOINT')
S3_ACCESS_KEY = getenv('S3_ACCESS_KEY')
S3_ACCESS_KEY_ID = getenv('S3_ACCESS_KEY_ID')
