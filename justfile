set dotenv-load := true

serve:
	uv run python3 -m edm_su_api

lint: ruff-lint mypy

ruff-lint:
	uv run ruff check --fix .

mypy:
	uv run mypy .

format: ruff-format

ruff-format:
	uv run ruff format .

unit-tests:
	uv run pytest tests/units/

integration-tests:
	uv run pytest tests/integration/

test: unit-tests integration-tests

preflight: unit-tests lint format

migrate-downgrade REVISION:
	uv run alembic downgrade "{{REVISION}}"

migrate:
	uv run alembic upgrade head

generate-migration MESSAGE:
	uv run alembic revision --autogenerate -m "{{MESSAGE}}"

generate-stubs:
	rm -rf typings/edm_su_api/
	uv run basedpyright --createstub edm_su_api
