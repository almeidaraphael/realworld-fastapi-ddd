export PYTHONPATH := .

# === Testing ===
test:
	poetry run pytest -x
test-cov:
	poetry run pytest --cov=app --cov-report=term-missing

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

# === Running Application ===
run:
	poetry run uvicorn app.main:app --reload

up-db:
	docker compose -p rw-demo-dev up -d db
	ENV_FILE=.env ./wait-for-it.sh $${POSTGRES_HOST}:$${POSTGRES_PORT} -- \
		poetry run alembic upgrade head

up-db-test:
	docker compose -p rw-demo-test up -d db_test
	ENV_FILE=.env.test ./wait-for-it.sh $${TEST_POSTGRES_HOST}:$${TEST_POSTGRES_PORT} -- \
		poetry run alembic upgrade head

down-db:
	docker compose -p rw-demo-dev down -v

down-db-test:
	docker compose -p rw-demo-test down -v

