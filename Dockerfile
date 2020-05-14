FROM python:3.7
ENV PYTHONBUFFERED 1

RUN mkdir /api
WORKDIR /api
COPY Pipfile /api/
COPY Pipfile.lock /api/
RUN pip3 install pipenv
RUN set -ex && pipenv install --deploy --system
RUN apt-get -q update && apt-get -qy install netcat

COPY . /api/