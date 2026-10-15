# Agent handoff — ClaimFlow

Read `AGENTS.md`, `README.md`, and `docs/PRD.md` first. Load other files only when the task requires them. Do not automatically call all skills or MCP tools.

## Current verified facts

- The initial Python backend has 8 passing automated tests.
- A Next.js TypeScript reviewer interface is written, but its package installation/build did not complete in the authoring environment because npm timed out.
- The only loaded data is synthetic; external APIs, claims decisions, and LLM calls are absent.

## Best next task

Run the frontend in a capable local environment and repair any build/runtime issues. Then verify the full user journey: seed synthetic case, read source-backed conflict findings, add a document, record a review note. Take screenshots only after executing the app, not by imagining the UI.

## Cross-platform model usage

- **Claude Code:** use your best available reasoning model for architecture/security review, and a faster coding model for bounded edits when appropriate.
- **Codex:** use your best available reasoning model for cross-service debugging and test reviews; use standard coding settings for straightforward changes.
- **Cursor:** route frontend/UI tasks to a coding model with repository context; follow the same `AGENTS.md` rules.

Choose actual provider model IDs **at execution time** based on the user's active plan, current model menu, and task complexity; do not hardcode an unavailable name. When handing off work across platforms, include the exact changed files, commands executed, current test status, and remaining blockers.

## Safety reminders

Never infer real insurance coverage from the synthetic checklist. Do not put personally identifying data into prompts, traces, fixture files, screenshots, or issue descriptions.
