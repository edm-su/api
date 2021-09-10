#!/usr/bin/env sh
/wait db:5432
alembic upgrade head
pytest