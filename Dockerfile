FROM ghcr.io/astral-sh/uv:python3.12-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.6.10 /uv /uvx /bin/

COPY . .

RUN addgroup -S neshast \
    && adduser -S neshast -G neshast -s /bin/bash \
    && chown -R neshast:neshast /app \
    && apk update \
    && apk add make \
    && uv sync --frozen

USER neshast

EXPOSE 8000
