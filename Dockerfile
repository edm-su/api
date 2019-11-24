FROM python:3.7-alpine
ENV PYTHONBUFFERED 1

RUN mkdir /api
WORKDIR /api
COPY requirements.txt /api/
RUN \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc make musl-dev postgresql-dev && \
    python3 -m pip install -r requirements.txt --no-cache-dir && \
    apk --purge del .build-deps

COPY . /api/