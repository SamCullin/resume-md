
uv sync --all-extras
uv run isort .
uv run black .
uv run flake8 .
uv run pytest