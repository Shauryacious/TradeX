.PHONY: install run dev test lint format clean docker-build docker-run docker-up docker-down

# Install dependencies
install:
	pip install -r requirements.txt

# Run server
run:
	python main.py

# Run in development mode
dev:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
test:
	pytest

# Lint code
lint:
	ruff check .

# Format code
format:
	black .

# Clean cache and temporary files
clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	rm -rf .pytest_cache
	rm -rf .ruff_cache

# Docker commands
docker-build:
	docker build -t tradex-server .

docker-run:
	docker run -p 8000:8000 --env-file .env tradex-server

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

# Setup (first time)
setup: install
	@if [ ! -f .env ]; then \
		echo "Creating .env file from .env.example..."; \
		cp .env.example .env; \
		echo "Please edit .env file with your API credentials"; \
	fi
	mkdir -p logs

