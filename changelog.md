# Changelog

All changes are logged per file. Append only — never rewrite history.

---

## Session: 2026-06-11

### Added
- `pyproject.toml` — replaced `requirements.txt`; added ruff and pytest config
- `.gitignore` — standard Python + uv ignores; `.env` and `data/` excluded
- `changelog.md` — session tracking initialized
- `CLAUDE.md` — project-level guidance for Claude Code

### Notes
- `requirements.txt` removed in favour of `pyproject.toml` (uv standard)
- Existing scripts (`structured_agent.py`, `structured_agent_v2.py`) are legacy learning examples
