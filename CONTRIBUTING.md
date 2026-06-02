# Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository and create a feature branch.
2. Run `pip install -r requirements-dev.txt`.
3. Write tests for new functionality.
4. Run `ruff check . && black . && pytest` — all must pass.
5. Open a pull request with a clear description.

## Development Setup

```bash
cp .env.example .env
# Fill in GROQ_API_KEY (free at console.groq.com)
# VECTOR_STORE=chroma works without any API key
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

## Code Style

- Python 3.11+
- `ruff` for linting, `black` for formatting
- Type hints on all public functions
- No hardcoded secrets
