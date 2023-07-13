lint:
	ruff src

lint-fix:
	black src
	ruff check --fix src
