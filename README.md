# API edm.su

## Требования

* Python >= 3.10
* PostgreSQL >= 9.6
* Poetry
* Meilisearch >= 0.26

## Установка

```shell
poetry install
alembic upgrade head
```

## Запуск

```shell
./entrypoint.sh
```

## Переменные окружения

| Переменная                | Обязателен |                  Описание                   |           Значение по умолчанию            |
|---------------------------|:----------:|:-------------------------------------------:|:------------------------------------------:|
| EMAIL_FROM                |     x      | EMAIL от которого будут отправляться письма |               noreply@edm.su               |
| SECRET_KEY                |     x      |            Секрет (**обязательно            |                                            |
| изменить**)               |            |                                             |                                            |
| STATIC_URL                |     x      |                Адрес статики                |         https://static.dev.edm.su          |
| DATABASE_URL              |     x      |              Адрес базы данных              | postgresql://postgres:postgres@db/postgres |                    
| FRONTEND_URL              |     x      |               Адрес фронтенда               |               https://edm.su               |
| DEBUG                     |            |              Включить отладку               |                   False                    |
| TESTING                   |            |                Режим тестов                 |                   False                    |
| MEILISEARCH_API_URL       |     x      |            Адрес api meilisearch            |           http://localhost:7700            |
| MEILISEARCH_API_KEY       |            |            Ключ api meilisearch             |                                            |
| MEILISEARCH_INDEX_POSTFIX |            |  Дополнение к адресу индексов meilisearch   |                                            |
| S3_BUCKET                 |     x      |            Название S3 хранилища            |                                            |
| S3_ENDPOINT               |     x      |              Конечная точка S3              |                                            |
| S3_ACCESS_KEY             |     x      |              Ключ доступа к S3              |                                            |
| S3_ACCESS_KEY_ID          |     x      |           Идентификатор ключа S3            |                                            |
| SMTP_SERVER               |     x      |             Адрес SMTP сервера              |                                            |
| SMTP_PORT                 |     x      |                  Порт SMTP                  |                                            |
| SMTP_USER                 |     x      |              Пользователь SMTP              |                                            |
| SMTP_PASSWORD             |     x      |                 Пароль SMTP                 |                                            |
