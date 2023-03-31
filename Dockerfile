FROM python:3.11.2-slim as python-base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.4.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"
ENV PYTHONPATH=/app
RUN apt-get update && apt-get --no-install-recommends -y install libpq-dev


FROM python-base as builder-base
RUN apt-get install --no-install-recommends -y \
    curl \
    build-essential
RUN curl -sSL https://install.python-poetry.org | python -

WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

RUN poetry install --only main
RUN pip install setuptools


FROM builder-base as development
ENV DEBUG=True
RUN poetry install
COPY . /app
WORKDIR /app

RUN chmod +x entrypoint.dev.sh

EXPOSE 8000
ENTRYPOINT ./entrypoint.dev.sh


FROM development as test
ENV DEBUG=True
ENV TEST=True
RUN chmod +x entrypoint.test.sh
ENTRYPOINT ./entrypoint.test.sh


FROM python-base as production
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY . /app
WORKDIR /app

RUN chmod +x entrypoint.sh

EXPOSE 8000
ENTRYPOINT ./entrypoint.sh