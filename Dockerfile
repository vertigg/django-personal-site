FROM mcr.microsoft.com/vscode/devcontainers/python:3.7

ENV PYTHONUNBUFFERED 1
RUN locale-gen C.UTF-8 || true
ENV LANG=C.UTF-8

RUN apt update \
    && apt install -y \
    g++ \
    gcc \
    python-dev \
    && mkdir /app

RUN git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf && ~/.fzf/install

WORKDIR /app

COPY Pipfile .
COPY Pipfile.lock .
RUN pip install --upgrade pip pipenv
RUN pipenv install --dev --system

COPY . /app
RUN python /app/manage.py migrate
RUN python /app/manage.py collectstatic --noinput