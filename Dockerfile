FROM python:3.11.3-slim as python-base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
ENV PYSETUP_PATH=/pysetup
ENV HOST=0.0.0.0
RUN apt-get update && apt-get --no-install-recommends -y install libpq-dev


FROM python-base as builder-base

RUN pip install poetry && poetry config virtualenvs.in-project true

WORKDIR $PYSETUP_PATH
COPY . ./

RUN poetry install --only main


FROM python-base as production
COPY --from=builder-base $PYSETUP_PATH /app
WORKDIR /app

EXPOSE 8000
ENTRYPOINT ["./.venv/bin/python", "-m", "app"]