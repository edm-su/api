FROM cgr.dev/chainguard/python:latest-dev as builder

ARG POETRY_VERSION="1.8.3"

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

ARG PYTHON_VERSION="3.12"

WORKDIR /app

COPY --from=builder "/home/nonroot/venv/lib/python${PYTHON_VERSION}/site-packages" "/home/nonroot/.local/lib/python${PYTHON_VERSION}/site-packages"
COPY --from=builder /app/app /app/app
COPY alembic.ini .
COPY alembic ./alembic/

EXPOSE 8000
ENTRYPOINT ["python", "-m", "app"]
