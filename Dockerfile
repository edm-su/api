FROM python:3.7-slim
ENV PYTHONUNBUFFERED 1

RUN mkdir /api
WORKDIR /api

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ADD . /api/