set dotenv-load := true

serve:
	uv run python3 -m edm_su_api

lint: ruff-lint mypy

ruff-lint:
	uvx ruff check --fix .

mypy:
	uvx mypy .

format: ruff-format

ruff-format:
	uvx ruff format .

unit-tests:
	uv run pytest tests/units/

integration-tests:
	uv run pytest tests/integration/

test: unit-tests integration-tests

migrate:
	uv run alembic upgrade head

generate-migration MESSAGE:
	uv run alembic revision --autogenerate -m "{{MESSAGE}}"
