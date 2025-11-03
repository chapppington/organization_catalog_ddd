DC = docker compose
STORAGES_FILE = docker_compose/storages.yaml
DB_CONTAINER = organization-catalog-postgres
LOGS = docker logs
ENV = --env-file .env
APP_FILE = docker_compose/app.yaml
APP_CONTAINER = organization-catalog-api


.PHONY: precommit 
precommit:
	pre-commit run --all-files

