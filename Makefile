export PYTHONPATH := .

# === Environment Management ===
.PHONY: check-env
check-env:
	@echo "Checking current environment configuration..."
	@echo "APP_ENV: $(APP_ENV)"
	@echo "ENV_FILE: $(ENV_FILE)"
	@python -c "from app.config.settings import get_database_settings; settings = get_database_settings(); print(f'Environment: {settings.environment}'); print(f'Database: {settings.postgres_db}'); print(f'URL: {settings.database_url}')"

# === Testing ===
test:
	poetry run pytest
test-failfast:
	poetry run pytest -x
test-verbose:
	poetry run pytest -v
test-coverage:
	poetry run pytest --cov=app --cov-report=term
test-log:
	poetry run pytest --disable-warnings > pytest_logs.txt 2>&1

# === Formatting & Linting ===
lint:
	poetry run ruff format .
	poetry run ruff check . --fix	
	poetry run mypy app/

mypy:
	poetry run mypy .

format:
	poetry run ruff format .

# === Database / Migrations ===
migration:
	poetry run alembic revision --autogenerate -m "$(msg)"

migrate:
	poetry run alembic upgrade head

migrate-test:
	APP_ENV=testing poetry run alembic upgrade head

# === Running Application ===
run:
	poetry run uvicorn app.main:app --reload

run-prod:
	APP_ENV=production poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000

# === Database Container Management ===
define up_db_template
	@echo "Starting $(3) database container..."
	docker compose -p $(2) up -d $(3)
	@echo "Waiting for database to be ready..."
	./wait-for-it.sh $$(grep POSTGRES_HOST $(1) | cut -d '=' -f2):$$(grep POSTGRES_PORT $(1) | cut -d '=' -f2) -- \
		echo "Database is ready!"
	@echo "Running migrations..."
	sh -c 'set -a; source $(1); set +a; \
		export DATABASE_URL="postgresql+asyncpg://$$POSTGRES_USER:$$POSTGRES_PASSWORD@$$POSTGRES_HOST:$$POSTGRES_PORT/$$POSTGRES_DB"; \
		poetry run alembic upgrade head'
	@echo "$(3) database setup complete!"
endef

define down_db_template
	@echo "Stopping $(1) database containers..."
	docker compose -p $(1) down -v
	@echo "$(1) database containers stopped and volumes removed."
endef

up-db:
	$(call up_db_template,$(CURDIR)/.env,rw-demo-dev,db)

up-db-test:
	$(call up_db_template,$(CURDIR)/.env.test,rw-demo-test,db_test)

down-db:
	$(call down_db_template,rw-demo-dev)

down-db-test:
	$(call down_db_template,rw-demo-test)

# === Full Development Setup ===
.PHONY: setup-dev
setup-dev: up-db up-db-test
	@echo "Development environment setup complete!"
	@echo "Run 'make run' to start the application"
	@echo "Run 'make test' to run tests"

.PHONY: clean
clean: down-db down-db-test
	@echo "Cleaning up development environment..."
	docker system prune -f
	@echo "Cleanup complete!"

# === Health Checks ===
.PHONY: health-db
health-db:
	@echo "Checking database health..."
	@APP_ENV=development python -c "from app.config.settings import get_database_settings; settings = get_database_settings(); print(f'Dev DB: {settings.postgres_db} - OK')" || echo "Dev DB: ERROR"

.PHONY: health-db-test
health-db-test:
	@echo "Checking test database health..."
	@APP_ENV=testing python -c "from app.config.settings import get_database_settings; settings = get_database_settings(); print(f'Test DB: {settings.postgres_db} - OK')" || echo "Test DB: ERROR"

.PHONY: health-all
health-all: health-db health-db-test check-env

# === Database Management ===
.PHONY: db-info
db-info:
	poetry run python scripts/db_manager.py info

.PHONY: db-info-test
db-info-test:
	APP_ENV=testing poetry run python scripts/db_manager.py info

.PHONY: db-check
db-check:
	poetry run python scripts/db_manager.py check

.PHONY: db-check-test
db-check-test:
	APP_ENV=testing poetry run python scripts/db_manager.py check

.PHONY: db-reset-test
db-reset-test:
	APP_ENV=testing poetry run python scripts/db_manager.py reset

