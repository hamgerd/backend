.PHONY: migrations migrate run shell superuser collectstatic worker codegen swagger help

python3 = uv run python3

help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo "  migrations  to create new migrations"
	@echo "  migrate     to apply migrations"
	@echo "  run         to run the server"
	@echo "  shell       to run the shell"
	@echo "  superuser   to create a superuser"

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

worker:
	uv run celery -A config worker -l info

codegen:
	java -jar ~/.local/bin/swagger-codegen-cli.jar generate --additional-properties modelPropertyNaming=original -i swagger.json -l typescript-axios -o .api

swagger:
	curl http://localhost:8000/swagger.json/ > swagger.json                                                                                                                              ─╯

populate:
	uv run python manage.py runscript populate