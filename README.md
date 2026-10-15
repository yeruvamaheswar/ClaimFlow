# ClaimFlow

**Evidence-aware AI operations, beginning with trustworthy software.**

ClaimFlow is an **independent, synthetic-data-only** portfolio project exploring how insurance case evidence can be assembled, checked, reviewed, and audited. It is **not affiliated with USAA or any insurer** and does **not** make claim coverage, settlement, denial, payment, fraud, or underwriting decisions.

> **Current status — Foundation / vertical slice v0.1:** Tested FastAPI + SQLAlchemy backend and a Next.js reviewer interface implementation (frontend build not yet verified in this environment). The prototype loads one synthetic auto claim, extracts explicitly labeled text fields with source-line references, identifies discrepancies across documents, records review notes, and maintains a basic activity history. **No LLM, PDF upload, RAG, authentication, production audit immutability, or external systems are implemented yet.**

## What you can demonstrate today

1. Load a synthetic case involving four conflicting evidence documents.
2. Inspect three types of discrepancy: incident-date variance, VIN variance, and repair-estimate variance.
3. See which document and line contributed each finding.
4. Add another synthetic text document and observe the findings update.
5. Save a review note and inspect the corresponding activity event.

**Important:** Different repair estimates may be entirely legitimate. A variance is a request for review, not a claim that fraud or an error occurred.

## Local setup

Requirements: **Python 3.11+**, **Node.js 22+**, and npm. The API defaults to **SQLite for ease of development**; PostgreSQL is the intended later target. These services run on your machine only after you execute the commands.

### Terminal 1 — API

```bash
cd ClaimFlow/backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
uvicorn app.main:app --reload --port 8000
```

API documentation: <http://localhost:8000/docs>  
Health check: <http://localhost:8000/health>

### Terminal 2 — web UI

```bash
cd ClaimFlow/frontend
npm install
npm run dev
```

Open <http://localhost:3000> and click **Load example claim**. If you use a different API address, copy `frontend/.env.example` to `frontend/.env.local` and edit the value. The API allows the origin `http://localhost:3000` by default.

### Test the backend

```bash
cd ClaimFlow/backend
source .venv/bin/activate
pytest -q
```

### Explore without the frontend

```bash
curl -X POST http://localhost:8000/api/v1/demo/seed
curl http://localhost:8000/api/v1/claims
```

## Project map

```text
ClaimFlow/
├── AGENTS.md                 Cross-platform coding-agent instructions
├── CLAUDE.md                Claude Code entry point
├── .cursor/rules/            Cursor rules
├── docs/
│   ├── PRD.md               Product scope, users, acceptance criteria
│   ├── architecture.md      Service boundaries and diagram
│   ├── evaluation-plan.md   What correctness means and how to measure it
│   ├── security.md          Prototype limitations and threat model
│   ├── roadmap.md           Sprint plan and milestones
│   ├── backlog.md           Prioritized engineering work
│   └── decisions/           Architecture decision records
├── backend/                 FastAPI endpoints, evidence rules, tests
├── frontend/                Next.js reviewer workspace
├── examples/                Synthetic input contract examples
└── .github/workflows/       CI for backend tests
```

## Architectural approach

- **Now:** conventional backend + traceable deterministic evidence extraction + well-defined human review boundary.
- **Next:** structured document ingestion, PostgreSQL migrations, tests, authentication and case-level permissions.
- **Then:** LLM-assisted extraction, grounded retrieval, orchestration checkpoints, adversarial evaluation, and deployment.
- **Never:** allow an LLM's output to grant itself authorization or independently adjudicate a real claim.

See [the PRD](docs/PRD.md), [architecture](docs/architecture.md), and [roadmap](docs/roadmap.md).

## Ethics and limitations

This is a demonstration environment with **no authentication**. Do not upload real customer names, policy numbers, VINs, personal information, or insurance documents. The API intentionally refuses to start under a non-demo environment name; that is a guardrail, not a production security control. The audit log is **not tamper-evident**. Sample policy/checklist logic does not establish actual coverage.

## Attribution and research

The idea emerged from independent research into public insurance-industry AI engineering needs. It is **not a USAA product**, is not officially endorsed, and requires no USAA data. Specific technical dependencies remain subject to licensing and release review before publication/deployment.

## License

MIT — see [LICENSE](LICENSE).
