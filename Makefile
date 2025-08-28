.PHONY: help migrations migrate run shell superuser collectstatic test test-coverage lint test-all worker codegen swagger populate denvmaker dev

uv = uv run
python3 = $(uv) python3

help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo "  migrations        to create new migrations"
	@echo "  migrate           to apply migrations"
	@echo "  run               to run the server"
	@echo "  shell             to run the shell"
	@echo "  superuser         to create a superuser"
	@echo "  collectstatic     to collect static files"
	@echo "  test              to run tests"
	@echo "  test-coverage     to run tests with coverage report"
	@echo "  lint              to run linting with flake8"
	@echo "  test-all          to run linting and tests with coverage"
	@echo "  worker            to run the celery worker"
	@echo "  codegen           to generate API client from swagger.json"
	@echo "  swagger          to fetch the swagger.json from the running server"
	@echo "  populate          to populate the database with initial data"
	@echo "  denvmaker         to create .env file for development"
	@echo "  dev               to run the development environment with docker-compose"

migrations:
	$(python3) manage.py makemigrations $(arg)

migrate:
	$(python3) manage.py migrate

run:
	$(python3) manage.py runserver $(address)

shell:
	$(python3) manage.py shell

superuser:
	$(python3) manage.py createsuperuser

collectstatic:
	$(python3) manage.py collectstatic --no-input

test:
	$(uv) pytest

test-coverage:
	$(python3) -m coverage run --source='.' manage.py test
	$(python3) -m coverage report

lint:
	$(python3) -m flake8 .

test-all: lint test-coverage

worker:
	uv run celery -A config worker -l info

codegen:
	java -jar ~/.local/bin/swagger-codegen-cli.jar generate --additional-properties modelPropertyNaming=original -i swagger.json -l typescript-axios -o .api

swagger:
	curl http://localhost:8000/api/v1/schema/ > swagger.json

populate:
	uv run python manage.py runscript populate

denvmaker: # development env file maker
	cat env/development/* >> .env

dev:
	docker compose --env-file env/development/django.env --env-file env/development/minio.env -f docker-compose-development.yaml up