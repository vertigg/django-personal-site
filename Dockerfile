FROM python:3.10.13-slim-bullseye
LABEL name=homesite-project version=dev maintainer="Vertig <vertigo.spy@gmail.com>"
ENV PYTHONUNBUFFERED 1
RUN locale-gen C.UTF-8 || true
ENV LANG=C.UTF-8

RUN apt update \
    && apt install -y \
    g++ \
    gcc \
    python-dev \
    && mkdir /app

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app
# RUN python /app/manage.py migrate
# RUN python /app/manage.py collectstatic --noinput
