FROM python:3.13.3-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
COPY uv.lock .
COPY README.md .
COPY pyproject.toml .
COPY src ./src
COPY alembic.ini .
COPY alembic ./alembic

RUN uv sync --no-dev --no-upgrade

EXPOSE 8000
ENTRYPOINT ["uv", "run", "--no-dev", "python", "-m"]
CMD ["edm_su_api"]
