#!/bin/bash

STATE=${NA_STATE:-$1}

case "$STATE" in
  development)
    cp .env.development .env
    cp docker-compose-development.yaml docker-compose.yaml 2>/dev/null || true
    echo "Set to development mode.";;
  stage)
    cp .env.stage .env
    cp docker-compose-stage.yaml docker-compose.yaml
    echo "Set to stage mode.";;
  production)
    cp .env.production .env
    cp docker-compose-production.yaml docker-compose.yaml 2>/dev/null || true
    echo "Set to production mode.";;
esac
