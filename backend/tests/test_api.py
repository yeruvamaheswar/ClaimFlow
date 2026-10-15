"""Minimal API integration tests; each test uses an isolated SQLite file (see conftest.py)."""


def test_demo_is_idempotent_and_contains_conflicts(client):
    first = client.post("/api/v1/demo/seed")
    assert first.status_code == 200
    payload = first.json()
    assert payload["document_count"] == 4
    expected = {"INCIDENT_DATE_VARIANCE", "VEHICLE_VIN_VARIANCE", "ESTIMATE_TOTAL_VARIANCE"}
    assert expected.issubset({finding["code"] for finding in payload["findings"]})
    second = client.post("/api/v1/demo/seed")
    assert second.json()["id"] == payload["id"]
    assert second.json()["document_count"] == 4


def test_claim_review_is_explicitly_not_a_claims_decision(client):
    created = client.post("/api/v1/claims", json={
        "claimant_label": "Synthetic Test Person",
        "policy_ref": "SYN-TEST-123", "incident_date": "2026-10-01",
    })
    assert created.status_code == 201
    claim_id = created.json()["id"]
    evidence = client.post(f"/api/v1/claims/{claim_id}/documents", json={
        "filename": "note.txt", "document_type": "claim_form",
        "text": "Incident Date: 2026-10-02",
    })
    assert evidence.status_code == 201
    assert any(f["code"] == "INCIDENT_DATE_VARIANCE" for f in evidence.json()["findings"])
    review = client.post(f"/api/v1/claims/{claim_id}/review", json={
        "note": "Reviewed conflicting incident date. Follow-up required."
    })
    assert review.status_code == 200
    audit = review.json()["audit_events"]
    assert audit[-1]["detail"]["decision_scope"] == "evidence_review_only"
    assert review.json()["status"] == "review_recorded"


def test_invalid_document_rejected(client):
    response = client.post("/api/v1/claims", json={
        "claimant_label": "Example Person", "policy_ref": "REAL-POLICY",
        "incident_date": "2026-10-01",
    })
    assert response.status_code == 422


def test_timestamps_are_explicit_utc_after_reload(client):
    created = client.post("/api/v1/claims", json={
        "claimant_label": "Synthetic Time Person",
        "policy_ref": "SYN-TIME-1", "incident_date": "2026-10-01",
    }).json()
    reloaded = client.get(f"/api/v1/claims/{created['id']}").json()
    assert reloaded["created_at"].endswith("+00:00")
    assert reloaded["audit_events"][0]["created_at"].endswith("+00:00")


def test_health(client):
    assert client.get("/health").json()["mode"] == "demo"
