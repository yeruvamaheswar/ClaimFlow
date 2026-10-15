# ADR-0001 — Deterministic-first vertical slice

**Status:** Accepted for v0.1 (2026-10-15)

## Context

The intended portfolio showcases enterprise AI engineering. There is temptation to start with several specialized agents, but without validated domain examples this would be fragile and difficult to assess.

## Decision

Build a working web/API/data vertical slice first, using explicit document field labels and deterministic discrepancy checks. Preserve evidence source locations from the outset. Introduce model-assisted extraction only after a baseline benchmark, then retrieval only with a versioned policy corpus and citation tests.

## Consequences

- Easier to test, explain, and demonstrate.
- Maintains a measurable baseline for future AI components.
- Does not yet demonstrate inference or genuine agentic orchestration; those are subsequent milestones and must be labeled honestly.
- Current SQLite/no-auth setup is strictly for local synthetic demos.
