.PHONY: dev down check test prod prod-down _docker

COMPOSE = docker compose --env-file $(ENV_FILE) -f docker-compose.yml
PROD_COMPOSE = docker compose --env-file .env -f docker-compose.prod.yml
MANAGE = $(COMPOSE) run --build --no-deps --rm web python manage.py
ENV_FILE = .env.development
DOCKER_WAIT = 90
ifdef PORT
export DJANGO_PORT = $(PORT)
endif

dev: _docker
	$(COMPOSE) up --build --remove-orphans

# Stop the dev services (SQLite volume is preserved).
down: _docker
	$(COMPOSE) down

check: _docker
	$(MANAGE) check

# Usage: make test T=orders.tests
test: _docker
	$(MANAGE) test $(T)

prod: _docker
	$(PROD_COMPOSE) up --build --wait

prod-down: _docker
	$(PROD_COMPOSE) down

# Make sure the Docker daemon is up; on macOS start Docker Desktop and wait for it.
_docker:
	@docker info >/dev/null 2>&1 && exit 0; \
	if [ "$$(uname)" = "Darwin" ]; then \
		echo "Starting Docker Desktop..."; \
		open -a Docker || exit 1; \
		for i in $$(seq $(DOCKER_WAIT)); do \
			docker info >/dev/null 2>&1 && echo "Docker is ready." && exit 0; \
			sleep 1; \
		done; \
		echo "Docker did not start within $(DOCKER_WAIT)s." >&2; exit 1; \
	else \
		echo "Docker is not running. Start the Docker daemon and retry." >&2; exit 1; \
	fi
