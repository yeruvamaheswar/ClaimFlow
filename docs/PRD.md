# ClaimFlow Product Requirements Document

**Status:** Approved initial direction; v0.1 prototype in progress  
**Product owner:** Independent portfolio project  
**Last revised:** 2026-10-15  
**Domain:** Synthetic auto-insurance evidence intake and exception review

## 1. Problem

Insurance case-review workflows often require employees to assemble disparate evidence, compare structured details, locate the source of a discrepancy, and document review actions. ClaimFlow is designed to **demonstrate** how evidence-aware software could assist such a workflow. These are domain hypotheses to investigate, **not assertions about USAA's private operations**.

## 2. Product promise

A reviewer can understand what information arrived, which fields disagree, exactly where each finding came from, and what still requires human follow-up. ClaimFlow provides explainable case preparation, not decision automation.

## 3. Users and jobs-to-be-done

- **Claims reviewer (demo persona):** Inspect a synthetic case and track discrepancies efficiently.
- **Operations supervisor (future persona):** Review exceptions and ensure appropriate escalation.
- **AI/platform engineer:** Understand, test, and monitor extraction, retrieval, and workflow reliability.

## 4. First scenario

A synthetic parking-lot accident with four plain-text documents:

1. Claim form: incident date September 18; synthetic VIN A.
2. Police report: incident date September 19; synthetic VIN A.
3. Repair estimate A: synthetic VIN A, estimated total $1,850.
4. Repair estimate B: synthetic VIN B, estimated total $2,275.

System flags date, VIN, and estimate variance with traceable source lines. It **does not select a winner, infer fraud, or decide coverage**.

## 5. v0.1 in scope

- Create a synthetic case and view list/detail.
- Add explicitly labeled plain-text evidence documents.
- Extract incident date, VIN, and estimate total through deterministic parsing.
- Track source filename, line number, and exact excerpt for extracted fields.
- Flag missing demonstration-checklist documents and evidence discrepancies.
- Record reviewer notes and activity events.
- Provide a polished, accessible case-review interface.
- Run repeatable backend tests, including a deliberately adversarial text fixture.

## 6. v0.1 out of scope

Real claims; external production integrations; claim settlement or fraud scoring; OCR; PDF extraction; LLM inference; vector retrieval; real-policy reasoning; advanced workflow orchestration; authentication; role-based authorization; cryptographically protected audit logs; hosted public deployment; regulated production use.

## 7. Acceptance criteria

| ID | Acceptance criterion | Status |
|---|---|---|
| AC-01 | Demo case loads only once and includes four synthetic documents. | Implemented; integration tested |
| AC-02 | Dates, VINs, and totals are extracted with source line and text. | Dates and VINs: implemented and unit tested. Totals: covered only by the seed integration test. |
| AC-03 | Conflicting source values produce review findings, not silent correction. | Implemented; unit and integration tested |
| AC-04 | New evidence refreshes case findings. | Implemented; integration tested |
| AC-05 | Reviewer note is recorded without making a claims decision. | Implemented; integration tested |
| AC-06 | Local backend and web client are easy to start. | Backend tests pass. Frontend typecheck and build verified 2026-10-15. |
| AC-07 | Real-user data is protected by production-grade access control. | NOT implemented, required before any real deployment |

## 8. Later milestones

- v0.2: support structured document/PDF ingestion with parser quality tests and safer storage.
- v0.3: PostgreSQL migration, case-level authorization, permissions test suite, and API hardening.
- v0.4: AI-assisted extraction with schema validation and factual-source alignment tests.
- v0.5: Retrieval for versioned **sample** policies, citation validation, and relevant/not-relevant benchmarks.
- v0.6: Stateful orchestrated reviews, approval boundaries, and failure recovery.
- v1.0 portfolio: metrics, diagrams, observability, release regression evaluation, deployment, demo video.

## 9. Success measures

Prototype measurements: field-level extraction precision/recall, source attribution accuracy, unauthorized tool-action count, retrieval validity (later), recovery-test pass rate, processing latency, and cost per task (later). Do not publish impact claims until measured against a documented baseline. Passing a synthetic test suite **does not establish production suitability**.
