FROM python:3.12.8-slim-bullseye
LABEL name=homesite-project version=dev maintainer="Vertig <vertigo.spy@gmail.com>"
ENV PYTHONUNBUFFERED 1
RUN locale-gen C.UTF-8 || true
ENV LANG=C.UTF-8

RUN apt update \
    && apt install -y --no-install-recommends \
    g++ \
    gcc \
    python-dev \
    curl \
    ca-certificates \
    libmagic1 \
    && mkdir /app

ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app

COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

COPY . /app
# RUN python /app/manage.py migrate
# RUN python /app/manage.py collectstatic --noinput
