FROM python:3-slim-stretch

ENV PYTHONUNBUFFERED 1

RUN apt update \
    && apt install -y \
    g++ \
    gcc \
    python-dev \
    && mkdir /app

WORKDIR /app

COPY Pipfile .
COPY Pipfile.lock .
RUN pip install --upgrade pip pipenv
RUN pipenv install --dev --system

COPY . /app
RUN python /app/manage.py migrate
RUN python /app/manage.py collectstatic --noinput