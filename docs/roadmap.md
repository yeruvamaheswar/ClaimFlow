# ClaimFlow implementation roadmap

The live plan is [plans/claimflow-onboarding.md](../plans/claimflow-onboarding.md). The sections below are the longer-term outline.

Assumes roughly 10–15 hours of project effort per week. The 15-week structure is indicative, not a delivery guarantee.

## Sprint 0 — Repository and first working slice (completed in this workspace)

- [x] New project directory and starter documentation
- [x] Python API and SQLite demonstration persistence
- [x] Synthetic demo case + evidence discrepancy engine
- [x] Initial automated backend tests (run `pytest -q`)
- [x] Initial Next.js workspace source and API wiring
- [x] Cross-platform agent guidance
- [x] Verify frontend installation/build (typecheck and build pass, 2026-10-15)
- [ ] Capture screenshots and review actual UI after launch
- [x] GitHub repository published

## Weeks 1–2 — Foundation and requirements refinement

- [ ] Validate claim-review persona, business case, and user journeys.
- [ ] Define complete sample-document ground truth and expected findings.
- [ ] Confirm API/data contracts, ADRs, and failure behaviors.
- [ ] Add frontend interaction tests and refined mobile accessibility.

## Weeks 3–5 — Small working MVP

- [ ] Implement safe, structured document ingestion (PDF/Docling or alternative).
- [ ] Add file metadata, source offsets, and a source-document viewer.
- [ ] Create an evidence and exception lifecycle with explicit reviewer state.
- [ ] Add PostgreSQL + migration tooling, plus reproducible local setup.

## Weeks 6–9 — AI engineering

- [ ] Baseline parser evaluation and golden benchmark cases.
- [ ] Add optional AI extraction behind schema validation and source alignment.
- [ ] Build a versioned sample-policy knowledge corpus.
- [ ] Implement filtered hybrid retrieval and evidence-citation checks.
- [ ] Add orchestration only where stateful AI workflow needs it.

## Weeks 10–13 — Enterprise controls

- [ ] Authentication, authorization, and case-level permission tests.
- [ ] Durable workflow checkpoints, safe retries, and idempotency tests.
- [ ] Adversarial tests, structured traces, model release comparison.
- [ ] Redaction and private document storage.
- [ ] Replace demonstration-only audit convention with protected design.

## Weeks 14–15 — Portfolio

- [ ] Stable demo deployment containing synthetic data only.
- [ ] 3–5 minute walkthrough and technical deep dive.
- [ ] Measured before/after benchmarks and limitations.
- [ ] Final architecture diagrams, developer documentation, security brief.
- [ ] Resume, interview stories, and independent outreach materials.

## Development rules

1. Keep one complete end-to-end slice working.
2. Introduce complexity only to satisfy a testable requirement.
3. Measure extraction correctness before asking AI to improve it.
4. No real claims processing or consequential autonomous decisions.
