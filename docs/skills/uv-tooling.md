# Skill: uv Python Environment & Dependency Management

System Python 3.10 must remain untouched because other projects depend on it.

This project uses project-local uv-managed Python 3.12.

Why:
- Django 6.0 supports Python 3.12–3.14.
- Django 5.2 is the last Django line supporting Python 3.10.

Initial workflow:

```bash
uv --version
uv self update
uv python install 3.12
uv venv --python 3.12 .venv
uv run python --version
```

Create `.python-version` with:
```text
3.12
```

Use uv project/dependency management:
```bash
uv init
uv add django
uv add --dev pytest ruff
uv sync
```

Prefer:
```bash
uv run python manage.py ...
uv run pytest
uv run ruff check .
uv run ruff format .
```

Do not use raw `pip install` as the normal project dependency workflow.
Do not modify unrelated Python installations/projects.

Commit:
- pyproject.toml
- uv.lock
- .python-version

Do not commit .venv.

Do not silently upgrade Python or dependencies during a phase. Verify compatibility and document decisions.
