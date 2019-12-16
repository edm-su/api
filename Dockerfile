FROM python:3.7-alpine
ENV PYTHONBUFFERED 1

RUN mkdir /api
WORKDIR /api
COPY Pipfile /api/
COPY Pipfile.lock /api/
RUN pip3 install pipenv
RUN \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc make musl-dev postgresql-dev && \
    set -ex && pipenv install --deploy --system && \
    apk --purge del .build-deps

COPY . /api/