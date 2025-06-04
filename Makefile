.PHONY: migrations migrate run shell superuser collectstatic worker codegen swagger help test test-coverage lint test-all

python3 = uv run python3

help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo "  migrations    to create new migrations"
	@echo "  migrate       to apply migrations"
	@echo "  run           to run the server"
	@echo "  shell         to run the shell"
	@echo "  superuser     to create a superuser"
	@echo "  test          to run tests"
	@echo "  test-coverage to run tests with coverage report"
	@echo "  lint          to run linting with flake8"
	@echo "  test-all      to run linting and tests with coverage"

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
	$(python3) manage.py test

worker:
	uv run celery -A config worker -l info

codegen:
	java -jar ~/.local/bin/swagger-codegen-cli.jar generate --additional-properties modelPropertyNaming=original -i swagger.json -l typescript-axios -o .api

swagger:
	curl http://localhost:8000/api/v1/swagger.json/ > swagger.json                                                                                                                              ─╯

populate:
	uv run python manage.py runscript populate

# Run tests with coverage report
test-coverage:
	$(python3) -m coverage run --source='.' manage.py test
	$(python3) -m coverage report

# Run linting with flake8
lint:
	$(python3) -m flake8 .

# Run linting and tests with coverage
test-all: lint test-coverage
