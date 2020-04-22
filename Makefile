check:
	poetry run mypy **/*.py
	poetry run pytype **/*.py
	poetry run pytest

test:
	poetry run pytest
