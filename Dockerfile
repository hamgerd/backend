FROM python:3.12-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.6.10 /uv /uvx /bin/

COPY . .

RUN useradd -ms /bin/bash neshast \
    && apt-get update \
    && apt-get install -y --no-install-recommends make \
    && rm -rf /var/lib/apt/lists/* \
    && uv sync --frozen

USER neshast

EXPOSE 8000
