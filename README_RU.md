# API edm.su

## Требования

* Python >= 3.10
* PostgreSQL >= 14

## Установка

```shell
pip install -r requirements.txt
alembic upgrade head
```

## Запуск

```shell
python3 -m edm_su_api
```

## Переменные окружения

| Переменная                | Обязателен |                                Описание                                |               Значение по умолчанию                |
| ------------------------- | :--------: | :--------------------------------------------------------------------: | :------------------------------------------------: |
| DATABASE_URL              |     x      |                           Адрес базы данных                            | postgresql+asyncpg://postgres:postgres@db/postgres |
| DISABLE_OPENAPI           |            |                        Режим отключения OpenAPI                        |                       False                        |
| HOST                      |            |                              Адрес хоста                               |                     127.0.0.1                      |
| LOG_LEVEL                 |            | Уровень логирования (может быть DEBUG, INFO, WARNING, ERROR, CRITICAL) |                       ERROR                        |
| PORT                      |            |                               Порт хоста                               |                        8000                        |
| S3_ACCESS_KEY             |     x      |                           Ключ доступа к S3                            |                                                    |
| S3_ACCESS_KEY_ID          |     x      |                         Идентификатор ключа S3                         |                                                    |
| S3_BUCKET                 |     x      |                         Название S3 хранилища                          |                                                    |
| S3_ENDPOINT               |     x      |                           Конечная точка S3                            |                                                    |
| S3_REGION                 |     x      |                               Регион S3                                |                     us-east-1                      |
| SPICEDB_API_KEY           |     x      |                            Spicedb api key                             |                                                    |
| SPICEDB_INSECURE          |            |              Режим безопасности для подключения к Spicedb              |                       False                        |
| SPICEDB_TLS_CERT          |            |                         Путь к сертификату TLS                         |                                                    |
| SPICEDB_URL               |     x      |                            Spicedb API URI                             |                                                    |
| STATIC_URL                |     x      |                             Адрес статики                              |             https://static.dev.edm.su              |
