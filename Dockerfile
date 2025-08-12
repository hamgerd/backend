FROM ghcr.io/astral-sh/uv:python3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.6.10 /uv /uvx /bin/

RUN addgroup -S neshast && adduser -S neshast -G neshast -s /bin/bash

RUN apk update && apk add make curl

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

COPY . .
RUN chown -R neshast:neshast /app

USER neshast

EXPOSE 8000
