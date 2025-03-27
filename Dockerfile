FROM python:3.12-slim-bullseye

RUN apt-get update && apt-get install -y --no-install-recommends \
    make

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.6.10 /uv /uvx /bin/

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

COPY . .