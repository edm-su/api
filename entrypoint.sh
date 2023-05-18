#!/usr/bin/env sh
alembic upgrade head
python app/main.py