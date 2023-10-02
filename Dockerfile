FROM cgr.dev/chainguard/python:latest-dev as builder

ARG POETRY_VERSION="1.6.1"
WORKDIR /app
COPY pyproject.toml poetry.lock README.md .
COPY app ./app

RUN python -m venv $HOME/tools && \
    . "${HOME}/tools/bin/activate" && \
    pip install "poetry==${POETRY_VERSION}"

RUN python -m venv "${HOME}/venv" && \
    . "${HOME}/venv/bin/activate" && \
    ~/tools/bin/poetry install --only main


FROM cgr.dev/chainguard/python:latest

WORKDIR /app

COPY --from=builder /home/nonroot/venv/lib/python3.11/site-packages /home/nonroot/.local/lib/python3.11/site-packages
COPY --from=builder /app/app /app/app
COPY alembic.ini .
COPY alembic ./alembic/

EXPOSE 8000
CMD ["-m", "app"]