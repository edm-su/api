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
| DISABLE_OPENAPI           |            |                              Disable OpenAPI                            |                   False                    |
| HOST                      |            |                             Host address                              |                   127.0.0.1                   |
| LOG_LEVEL                 |            | Log level (can be DEBUG, INFO, WARNING, ERROR, CRITICAL) |                  ERROR                   |
| MEILISEARCH_API_KEY       |            |                          Meilisearch api key                          |                                            |
| MEILISEARCH_API_URL       |     x      |                         Meilisearch API URI                          |           http://localhost:7700            |
| MEILISEARCH_INDEX_POSTFIX |            |                Meilisearch index postfix                         |                         |                                            |
| PORT                      |            |                             Port address                              |                   8000                      |
| S3_ACCESS_KEY             |     x      |                           S3 access key                            |                                            |
| S3_ACCESS_KEY_ID          |     x      |                         S3 access key ID                         |                                            |
| S3_BUCKET                 |     x      |                         S3 bucket name                          |                                            |
| S3_ENDPOINT               |     x      |                           S3 endpoint                            |                                            |
| S3_REGION                 |     x      |                               S3 region                                |                 us-east-1                  |
| SPICEDB_API_KEY           |     x      |                           Spicedb api key                          |                                            |
| SPICEDB_URL               |     x      |                           Spicedb API URI                          |                                             |
| STATIC_URL                |     x      |                             Static URL                              |         https://static.dev.edm.su          |
