# Prioritized backlog

## P0 — Next engineering session

1. Run `npm install` and `npm run build` for web UI; address any TypeScript/runtime errors.
2. Manual browser acceptance check with synthetic demo case; verify responsive layout.
3. Improve test DB isolation, request logging, structured response schemas, and API error messages.
4. Implement edit/view for original text evidence (not only extracted field summaries).
5. Add a short engineering demo and annotated design notes.

## P1 — MVP

6. Document ingestion pipeline with file size/type validation and source-location preservation.
7. Versioned schema + Alembic/PostgreSQL migration.
8. Reviewer action workflow with status transition rules and optimistic locking.
9. Evaluation corpus with labeled provenance and expected discrepancies.
10. Case-level authentication and backend authorization before deploying shared environments.

## P2 — AI and enterprise controls

11. LLM extraction comparison against baseline; enforce typed outputs.
12. Versioned synthetic policy corpus, hybrid RAG, filtered retrieval, citation scoring.
13. Workflow checkpoints, idempotent side effects, and recovery scenarios.
14. Traceability, costs, latency dashboards, and adversarial evaluation.
15. Public synthetic-only portfolio deployment and demo narrative.

## Explicitly not now

Real insurer APIs, fraud accusations, production claims automation, custom LLM fine-tuning, Kubernetes, complex multi-agent choreography, and real PII.
