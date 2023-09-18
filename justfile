set dotenv-load := true

serve:
	poetry run python app/main.py

lint: ruff-lint mypy black-lint

ruff-lint:
	poetry run ruff check .

mypy:
	poetry run mypy .

black-lint:
	poetry run black . --check

format: ruff-format black-format

ruff-format:
	poetry run ruff check --fix .

black-format:
	poetry run black .

unit-tests:
	poetry run pytest tests/units/

integration-tests:
	poetry run pytest tests/integration/

test: unit-tests integration-tests

install:
	poetry install --with lint

migrate:
	poetry run alembic upgrade HEAD

generate-migration:
	poetry run alembic revision --autogenerate