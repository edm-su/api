FROM python:3.12-slim-bullseye as python

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

FROM python as dependencies

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV VIRTUAL_ENV=/opt/venv

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

COPY ./requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip --mount=type=cache,target=/root/.cache/uv \
  python -m pip config --user set global.progress_bar off && \
  uv venv /opt/venv && \
  uv pip install --requirement requirements.txt

FROM python

WORKDIR /app

COPY --from=dependencies /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH=$PYTHONPATH:/app/src

COPY alembic.ini .
COPY alembic ./alembic
COPY src ./src

EXPOSE 8000
ENTRYPOINT ["python", "-m"]
CMD ["edm_su_api"]
