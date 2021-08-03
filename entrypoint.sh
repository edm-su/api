#!/usr/bin/env sh
alembic upgrade head
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0 -w 1