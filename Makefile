.PHONY: build up down restart ps logs shell test generate-data run-pipeline api verify help

help:
	@echo "Available commands:"
	@echo "  make build            - Build Docker images"
	@echo "  make up               - Start all services"
	@echo "  make down             - Stop all services"
	@echo "  make restart          - Restart all services"
	@echo "  make ps               - Show running services"
	@echo "  make logs             - View logs from all services"
	@echo "  make shell            - Open a shell in the app container"
	@echo "  make test             - Run tests"
	@echo "  make generate-data    - Generate sample data for testing"
	@echo "  make run-pipeline     - Run the complete pipeline"
	@echo "  make verify           - Verify pipeline results"
	@echo "  make api              - Start only the API service"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

ps:
	docker-compose ps

logs:
	docker-compose logs -f

shell:
	docker-compose run --rm app /bin/bash

test:
	docker-compose run --rm app python -m pytest

generate-data:
	docker-compose run --rm app python -m scripts.generate_sample

run-pipeline:
	docker-compose run --rm app python -m src.pipeline.orchestrator

verify:
	docker-compose run --rm app python ./verify_results.py

api:
	docker-compose up -d api 