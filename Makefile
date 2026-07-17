.PHONY: build-scaffold check-scaffold clean-scaffold lint test ci

build-scaffold:
	python3 scripts/build-scaffold.py

check-scaffold:
	python3 scripts/build-scaffold.py --check

clean-scaffold:
	python3 scripts/build-scaffold.py --clean

lint:
	uv run --project packages/llmzk-tools ruff check packages/llmzk-tools/src packages/llmzk-tools/tests scripts/build-scaffold.py tests/integration

test:
	uv run --project packages/llmzk-tools pytest packages/llmzk-tools/tests tests/integration

ci: lint test build-scaffold check-scaffold
