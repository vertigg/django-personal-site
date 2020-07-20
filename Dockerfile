FROM python:3.7.7-buster
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

RUN git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf && ~/.fzf/install

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app
RUN python /app/manage.py migrate
RUN python /app/manage.py collectstatic --noinput

ENV DJANGO_DEBUG=true