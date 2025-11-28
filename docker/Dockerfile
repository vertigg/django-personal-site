FROM python:3.12-slim-bookworm AS builder 
LABEL name=homesite-project version=dev maintainer="Vertig <vertigo.spy@gmail.com>"
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev --no-install-project
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev


FROM python:3.12-slim-bookworm AS runtime
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 
RUN apt update && apt install -y --no-install-recommends libmagic1
WORKDIR /app
COPY --from=builder /app /app

# RUN python /app/manage.py migrate
# RUN python /app/manage.py collectstatic --noinput
