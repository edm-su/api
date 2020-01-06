from os import getenv

EMAIL_FROM = getenv('EMAIL_FROM', 'noreply@edm.su')

SECRET_KEY = getenv('SECRET_KEY', 'bhdasbdashjcxjhzbjhdasjhdasdbasj')

DB_DRIVER = getenv('DB_DRIVER', 'postgresql')
DB_USERNAME = getenv('DB_USERNAME', 'postgres')
DB_PASSWORD = getenv('DB_PASSWORD', ' ')
DB_HOST = getenv('DB_HOST', 'db')
DB_PORT = getenv('DB_PORT', 5432)
DB_NAME = getenv('DB_NAME', 'postgres')
