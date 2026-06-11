# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Folder Structure

```
TheStructuredAgent/
│   .env
│   pyproject.toml
│   changelog.md
│   CLAUDE.md
│   Dockerfile
│   docker-compose.yml
│   structured_agent.py          # legacy — Tax Clause Helper (v1)
│   structured_agent_v2.py       # legacy — Invoice Data Extractor (v2)
│
├───.github/
│   └───workflows/
│           ci.yml               # lint + test on every PR
│           cd.yml               # build + tag Docker on merge to main
│
├───app/
│   │   main.py
│   ├───api/
│   │   │   __init__.py
│   │   └───v1/
│   │       └───endpoints/
│   │               __init__.py
│   ├───models/
│   │       __init__.py
│   ├───services/
│   └───utils/
│
├───logs/
├───tests/
│   └───queries/                 # chatbot behavior test queries per feature
└───data/
```

When adding new files, register them here with an inline comment describing purpose.

---

## Protected Files

**Never modify without explicit user instruction:**
- `.env`
- `data/` folder (entire directory)
- `changelog.md` — append only, never rewrite history

**Restricted — only update when explicitly asked:**
- `pyproject.toml` — use `uv add <package>`, never manual edits without approval

---

## Setup

```bash
uv sync
```

Set `ANTHROPIC_API_KEY` in `.env` at the project root.

To add a dependency:
```bash
uv add <package>
```

---

## Running the API

```bash
uv run uvicorn app.main:app --reload
```

Legacy scripts (learning examples only — new features go as FastAPI endpoints):
```bash
uv run python structured_agent.py       # Tax Clause Helper (v1)
uv run python structured_agent_v2.py    # Invoice Data Extractor (v2)
```

---

## Architecture

**Current state:** Two standalone learning scripts demonstrating structured output parsing with the Anthropic SDK and Pydantic.

**Going forward:** All new features are FastAPI endpoints under `app/api/v1/endpoints/` — no new standalone scripts.

**Core pattern (both scripts):**
1. Define a Pydantic model for the expected output schema
2. Call `client.messages.parse()` with the model as `response_format`
3. Access the validated, typed result directly

**v1 (`structured_agent.py`):** Extracts Indian Tax Law clause data into a `TaxClause` Pydantic model.

**v2 (`structured_agent_v2.py`):** Invoice data extractor with custom validators (GSTIN = 15 chars, amount > 0) and a retry loop — validation errors are fed back to the model, up to 3 attempts.

Both scripts use `claude-sonnet-4-5` via the Anthropic Python SDK.

---

## Versioning Convention

- New endpoint versions go under `app/api/v2/endpoints/`
- If adding a new script variant (legacy path only): follow `structured_agent_v3.py` pattern and register above

---

## Model Upgrade Rule

- Scripts are hardcoded to `claude-sonnet-4-5`
- Flag to user when a newer model is available — do not upgrade without approval

---

## Known Issues / Gotchas

- `client.messages.parse()` is a beta feature — behaviour may change across SDK versions
- GSTIN validator in v2 enforces exactly 15 characters — test with valid Indian GSTIN format

---

## Linting

Run before every commit:
```bash
uv run ruff check .
uv run ruff format .
```

---

## Testing

```bash
uv run pytest                          # all tests
uv run pytest tests/<file>.py          # single file
```

Tests live in `tests/`. Feature test queries live in `tests/queries/<feature_name>_test_queries.md`.

Every new feature must include test queries covering:
- Happy path
- Edge cases (boundary values, empty input, unexpected format)
- Adversarial/negative cases (wrong type, missing fields, malformed data)

---

## CI/CD — GitHub Actions

**ci.yml** — triggers on every PR to `main`:
```yaml
- uv sync
- uv run ruff check .
- uv run pytest
```

**cd.yml** — triggers on merge to `main`:
```yaml
- Build Docker image
- Tag with commit SHA and `latest`
- Push to registry
```

Deployment step is TBD — local-first for now.

---

## Git & GitHub Workflow

**Remote:** `https://github.com/shivranjank/TheStructuredAgent.git`
**Default branch:** `main`
**Merge strategy:** Squash merge only

### Branch Naming
| Type | Pattern | Example |
|---|---|---|
| New feature | `feature/<name>` | `feature/invoice-extractor-v3` |
| Bug fix | `fix/<name>` | `fix/gstin-validator` |
| Maintenance | `chore/<name>` | `chore/update-dependencies` |

### First-Time Setup
```bash
git init
git remote add origin https://github.com/shivranjank/TheStructuredAgent.git
git branch -M main
```

### Daily Push Workflow
```bash
git checkout -b feature/<name>         # create branch
uv run ruff check . && uv run pytest   # lint + test before staging
git add <specific-files>               # never git add .
git commit -m "feat: description"      # follow commit format
git push -u origin feature/<name>      # push branch — confirm with user first
```

### Raising a PR
```bash
gh pr create --title "type: description" --base main --head feature/<name>
```
- Always squash merge on GitHub
- Delete branch after merge

### PR Checklist (before raising)
- [ ] `ruff check .` passes
- [ ] `pytest` passes
- [ ] `/code-review` run and findings addressed
- [ ] `changelog.md` updated for all changed files
- [ ] `README.md` reviewed and updated if affected
- [ ] No `.env` or `data/` files staged

---

## README Check

Every time any code file is changed:
1. Check if `README.md` exists at the project root
2. If it exists — review and update affected sections
3. If it does not exist — flag to user and ask if it should be created

---

## Changelog

All session changes logged in `changelog.md` — one entry per file changed, append only.
