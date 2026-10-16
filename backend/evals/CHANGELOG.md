# Gold corpus changelog

## corpus_version v0 — 2026-10-15

First 12 cases, format `case/1`. Fields: `incident_date`, `vehicle_vin`, `estimate_total`. Written without consulting any extractor.

| case_id | split | state |
|---|---|---|
| syn-001-clean-labeled | dev | labeled |
| syn-002-synonym-labels | dev | labeled |
| syn-003-date-conflict | dev | labeled |
| syn-004-vin-conflict | dev | labeled |
| syn-005-two-shop-estimates | dev | labeled |
| syn-006-missing-police-report | dev | labeled |
| syn-007-chain-collision | dev | todo (user labels) |
| syn-008-mirror | dev | todo (user labels) |
| syn-009-within-doc-conflict | holdout | labeled |
| syn-010-injection | holdout | labeled |
| syn-011-zero-documents | holdout | labeled |
| syn-012-supplement | holdout | todo (user labels) |
