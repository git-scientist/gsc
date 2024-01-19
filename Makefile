check: mypy test

mypy:
	poetry run mypy gsc tests

test:
	poetry run pytest
