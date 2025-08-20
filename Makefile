
.PHONY: setup run lint test format

setup:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt && pip install -r requirements-dev.txt

run:
	streamlit run app.py

lint:
	flake8 && black --check .

format:
	black .

test:
	pytest -q
