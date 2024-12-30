local-api-run: 
	uv run fastapi dev main.py

local-migrations:
	uv run alembic revision --autogenerate -m "$(MESSAGE)"

local-migrate:
	uv run alembic upgrade head

local-migrate-rollback:
	uv run alembic downgrade -1