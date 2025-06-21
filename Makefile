export PYTHONPATH := .

# === Formatting & Linting ===
lint:
	poetry run ruff format .
	poetry run ruff check . --fix
	poetry run mypy app/

mypy:
	poetry run mypy .

format:
	poetry run ruff format .

# === Running Application ===
run:
	poetry run uvicorn app.main:app --reload

