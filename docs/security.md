# Security constraints and initial threat model

## NON-PRODUCTION DEMONSTRATOR

**Do not deploy this release with public access or real data.** It has no authentication, authorization, rate limiting, durable secrets handling, or production audit guarantees.

## Assets and risks

| Asset / concern | Current treatment | Required later |
|---|---|---|
| Real personal or claims data | Forbidden by scope; no real data provided | Data minimization, consent/lawful basis, controls |
| User identity | Not collected or verified | Authentication, session management |
| Case access | No access controls in demo | Tenant/case-level authorization and negative tests |
| Uploaded documents | Plain-text bodies only, capped at 50k chars, stored locally | Malware scanning, parser isolation, object-storage permissions, size/type controls |
| Document prompt injection | No LLM or tool execution in v0.1 | Isolation of untrusted content, tool allowlists, red-team tests |
| Audit events | Application DB events; modifiable by DB administrator | Dedicated protected sink, append-only guarantees, retention policy |
| Claims outcome | No adjudication endpoints | Maintain authorization boundary even when downstream actions added |
| Model calls | None | Secret storage, redaction, telemetry controls, vendor retention review |
| Network exposure | Intended for localhost | TLS, CORS policy, auth, request limits, perimeter controls |

## Security tests to add before v0.3

- Cross-case document access denied for unauthorized user.
- Privileged mutations denied without appropriate role and explicit human action.
- Prompt injection in evidence cannot alter server permissions or tool call arguments.
- No PII in diagnostic logs.
- Uploaded files cannot execute code or escape storage boundaries.
- Retry of external action cannot duplicate effects.

## Important distinction

An LLM's declaration that a user is authorized is **never evidence of authorization**. Enforce permissions in the application backend, not in prompt text.
