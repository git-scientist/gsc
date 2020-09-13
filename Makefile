check: mypy pytype test

mypy:
	poetry run mypy gsc tests

pytype:
	poetry run pytype gsc tests

test:
	poetry run pytest
