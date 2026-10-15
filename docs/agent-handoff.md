# Agent handoff — ClaimFlow

Purpose: record what each slice changed, so the next agent or person can continue. Read `AGENTS.md`, `README.md`, and the live plan first.

Current state (2026-10-15): the frontend builds. CI is green on GitHub. The live plan is `plans/claimflow-onboarding.md`.

## Entry template

```text
### YYYY-MM-DD — Slice name
- Files changed:
- Commands run:
- Results:
- Actual hours:
- Open items:
```

## Entries

### 2026-10-15 — Slice 1: Hygiene and safe tests
- Files changed: `backend/tests/conftest.py` (new), `backend/tests/test_api.py`, `backend/tests/test_schema_version.py` (new), `backend/app/database.py`, `backend/app/main.py`, `frontend/package.json` (typecheck runs `next typegen` first), `.gitignore`, `CLAUDE.md`, `AGENTS.md`, `README.md`, `docs/*`. Removed `QUICKSTART_MAC.md`; untracked `frontend/tsconfig.tsbuildinfo` and `frontend/next-env.d.ts` (both generated).
- Commands run: `ruff check .`, `pytest -q` (full suite and each file alone), `npm run typecheck`, `npm run build`, `next dev`, `git status --porcelain`, `shasum -a 256 backend/claimflow.db`.
- Results: ruff clean; full suite and each test file pass alone; dev DB checksum unchanged by tests; git clean after typecheck, build, and dev. Tests use a fresh SQLite file per test. Startup refuses a mismatched schema version.
- Actual hours: about 0.5 (agent-built; review by lead).
- Open items: each test run still leaves one unused `claimflow_unused_<pid>.db` in the system temp dir (the app's startup hook touches it). Starlette's httpx test-client deprecation warning remains.

## Safety reminders

Never infer real insurance coverage from the synthetic checklist. Do not put personal data into prompts, traces, fixtures, screenshots, or issues.
