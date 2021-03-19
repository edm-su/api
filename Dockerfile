FROM python:3.9-alpine
ENV PYTHONUNBUFFERED 1

RUN mkdir /api
WORKDIR /api

COPY requirements.txt ./
RUN \
    apk add --no-cache postgresql-libs jpeg-dev zlib-dev && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev make g++ && \
    pip install --no-cache-dir -r requirements.txt && \
    apk --purge del .build-deps

ADD . /api/

CMD gunicorn app.main:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
EXPOSE 8000