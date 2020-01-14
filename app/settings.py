from os import getenv

EMAIL_FROM = getenv('EMAIL_FROM', 'noreply@edm.su')

SECRET_KEY = getenv('SECRET_KEY', 'bhdasbdashjcxjhzbjhdasjhdasdbasj')

DB_DRIVER = getenv('DB_DRIVER', 'postgresql')
DB_USERNAME = getenv('DB_USERNAME', 'postgres')
DB_PASSWORD = getenv('DB_PASSWORD', ' ')
DB_HOST = getenv('DB_HOST', 'db')
DB_PORT = getenv('DB_PORT', 5432)
DB_NAME = getenv('DB_NAME', 'postgres')

FRONTEND_URL = getenv('FRONTEND_URL', 'https://edm.su')

SENDGRID_API_KEY = getenv('SENDGRID_API_KEY')

YOUTUBE_API_KEY = getenv('YOUTUBE_API_KEY')

ALGOLIA_APP_ID = getenv('ALGOLIA_APP_ID')
ALGOLIA_API_KEY = getenv('ALGOLIA_API_KEY')
ALGOLIA_INDEX = getenv('ALGOLIA_INDEX')
