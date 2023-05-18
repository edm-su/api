# API edm.su

## Requirements

* Python >= 3.10
* PostgreSQL >= 9.6
* Poetry
* Meilisearch >= 1.0.0

## Install

```shell
poetry install
alembic upgrade head
```

## Run

```shell
./entrypoint.sh
```

## Environment variables

| Name                | Is required |                                Description                                |           Default value            |
|---------------------------|:----------:|:----------------------------------------------------------------------:|:------------------------------------------:|
| DATABASE_URL              |     x      |                           Postgres database address                            | postgresql://postgres:postgres@db/postgres |
| LOG_LEVEL                 |            | Log level (can be DEBUG, INFO, WARNING, ERROR, CRITICAL) |                  WARNING                   |
| EMAIL_FROM                |     x      |              EMAIL from which will be sent emails                           |               |               noreply@edm.su               |
| FRONTEND_URL              |     x      |                            Frontend URL                             |               https://edm.su               |
| MEILISEARCH_API_KEY       |            |                          Meilisearch api key                          |                                            |
| MEILISEARCH_API_URL       |     x      |                         Meilisearch API URI                          |           http://localhost:7700            |
| MEILISEARCH_INDEX_POSTFIX |            |                Meilisearch index postfix                         |                         |                                            |
| S3_ACCESS_KEY             |     x      |                           S3 access key                            |                                            |
| S3_ACCESS_KEY_ID          |     x      |                         S3 access key ID                         |                                            |
| S3_BUCKET                 |     x      |                         S3 bucket name                          |                                            |
| S3_ENDPOINT               |     x      |                           S3 endpoint                            |                                            |
| S3_REGION                 |     x      |                               S3 region                                |                 us-east-1                  |
| SECRET_KEY                |     x      |                         Secret key                          |                                            |
| SMTP_PASSWORD             |     x      |                              SMTP password                               |                                            |
| SMTP_PORT                 |     x      |                               SMTP port                                |                                            |
| SMTP_SERVER               |     x      |                           SMTP server                           |                                            |
| SMTP_USER                 |     x      |                           SMTP user                                |                                           |                                            |
| STATIC_URL                |     x      |                             Static URL                              |         https://static.dev.edm.su          |
| TESTING                   |            |                              Test mode                              |                   False                    |
| DEBUG                     |            |                              Debug mode                              |                   False                    |
