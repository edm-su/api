set dotenv-load := true

serve:
	poetry run app

lint: ruff-lint mypy

ruff-lint:
	poetry run ruff check --fix .

mypy:
	poetry run mypy .

format: ruff-format

ruff-format:
	poetry run ruff format .

unit-tests:
	poetry run pytest tests/units/

integration-tests:
	poetry run pytest tests/integration/

test: unit-tests integration-tests

install:
	poetry install --with lint

migrate:
	poetry run alembic upgrade head

generate-migration MESSAGE:
	poetry run alembic revision --autogenerate -m "{{MESSAGE}}"