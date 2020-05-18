#!/usr/bin/env bash

./wait-for db:5432
alembic upgrade head
pytest -s