
# Contributing

Thanks for taking the time to contribute!

## Dev Setup
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
pre-commit install
```

## Run
```bash
streamlit run app.py
```

## Tests & Lint
```bash
pytest -q
flake8
black --check .
```

## Commit Style
Use conventional commits if possible (e.g., `feat: add EV filter`). Small, focused PRs are easiest to review.
