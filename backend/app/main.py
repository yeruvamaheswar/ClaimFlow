"""ClaimFlow demonstration API. Intentionally no authentication: NOT FOR REAL DATA."""

import os
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .database import Base, engine, get_db
from .evidence import extract_facts, generate_findings
from .models import AuditEvent, Claim, Document
from .schemas import ClaimCreate, DocumentCreate, ReviewCreate

if os.getenv("CLAIMFLOW_ENV", "demo") != "demo":
    raise RuntimeError(
        "Only DEMO mode is implemented. Production requires authentication and security review."
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # Demo-only bootstrap; replace with migrations later.
    yield


app = FastAPI(
    title="ClaimFlow — Synthetic Insurance Evidence API",
    version="0.1.0",
    description="Demonstration only. Do not upload real personal, claim, or insurance data.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("CLAIMFLOW_WEB_ORIGIN", "http://localhost:3000")],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


def get_claim(db: Session, claim_id: str) -> Claim:
    claim = db.scalars(
        select(Claim).options(selectinload(Claim.documents), selectinload(Claim.audit_events))
        .where(Claim.id == claim_id)
    ).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim


def claim_view(claim: Claim) -> dict:
    findings = generate_findings(claim)
    return {
        "id": claim.id, "claim_ref": claim.claim_ref,
        "claimant_label": claim.claimant_label, "policy_ref": claim.policy_ref,
        "incident_date": claim.incident_date, "status": claim.status,
        "created_at": claim.created_at.isoformat(),
        "document_count": len(claim.documents), "finding_count": len(findings),
        "documents": [
            {
                "id": d.id, "filename": d.filename, "document_type": d.document_type,
                "extracted_facts": d.extracted_facts,
                "created_at": d.created_at.isoformat(),
            } for d in claim.documents
        ],
        "findings": findings,
        "audit_events": [
            {"id": e.id, "action": e.action, "detail": e.detail,
             "created_at": e.created_at.isoformat()} for e in claim.audit_events
        ],
    }


@app.get("/health")
def health():
    return {"status": "ok", "mode": "demo", "version": "0.1.0"}


@app.get("/api/v1/claims")
def list_claims(db: Session = Depends(get_db)):
    claims = db.scalars(
        select(Claim).options(selectinload(Claim.documents)).order_by(Claim.created_at.desc())
    ).all()
    return [
        {
            "id": c.id, "claim_ref": c.claim_ref, "claimant_label": c.claimant_label,
            "incident_date": c.incident_date, "status": c.status,
            "document_count": len(c.documents), "finding_count": len(generate_findings(c)),
        } for c in claims
    ]


@app.post("/api/v1/claims", status_code=201)
def create_claim(payload: ClaimCreate, db: Session = Depends(get_db)):
    claim = Claim(
        claim_ref="CF-" + uuid4().hex[:8].upper(),
        claimant_label=payload.claimant_label,
        policy_ref=payload.policy_ref,
        incident_date=payload.incident_date.isoformat(),
    )
    db.add(claim)
    db.flush()
    db.add(AuditEvent(claim_id=claim.id, action="claim.created", detail={"mode": "demo"}))
    db.commit()
    db.expire_all()  # Refresh eagerly-loaded relations before serializing.
    return claim_view(get_claim(db, claim.id))


@app.get("/api/v1/claims/{claim_id}")
def read_claim(claim_id: str, db: Session = Depends(get_db)):
    return claim_view(get_claim(db, claim_id))


@app.post("/api/v1/claims/{claim_id}/documents", status_code=201)
def add_document(claim_id: str, payload: DocumentCreate, db: Session = Depends(get_db)):
    claim = get_claim(db, claim_id)
    facts = extract_facts(payload.text)
    doc = Document(
        claim_id=claim.id, filename=payload.filename,
        document_type=payload.document_type, text=payload.text,
        extracted_facts=facts,
    )
    db.add(doc)
    claim.status = "review_required"
    db.add(AuditEvent(
        claim_id=claim.id, action="document.added",
        detail={"filename": payload.filename, "type": payload.document_type,
                "fields_extracted": sorted(facts)},
    ))
    db.commit()
    db.expire_all()  # Refresh eagerly-loaded relations before serializing.
    return claim_view(get_claim(db, claim.id))


@app.post("/api/v1/claims/{claim_id}/review")
def record_review(claim_id: str, payload: ReviewCreate, db: Session = Depends(get_db)):
    claim = get_claim(db, claim_id)
    claim.status = "review_recorded"
    db.add(AuditEvent(
        claim_id=claim.id, action="review.note_recorded",
        detail={"note": payload.note, "decision_scope": "evidence_review_only"},
    ))
    db.commit()
    db.expire_all()  # Refresh eagerly-loaded relations before serializing.
    return claim_view(get_claim(db, claim.id))


DEMO_DOCS = [
    ("claim-intake.txt", "claim_form", """Synthetic claim form — demonstration only
Incident Date: 2026-09-18
VIN: 4T1BE46K79U123456
Statement: Minor parking-lot collision; vehicle rear bumper impacted.
"""),
    ("police-report.txt", "police_report", """Synthetic incident report — demonstration only
Case Reference: DEMO-PO-01
Incident Date: 2026-09-19
VIN: 4T1BE46K79U123456
Narrative: Rear bumper damage observed.
"""),
    ("repair-estimate-a.txt", "repair_estimate", """Synthetic repair estimate A — demonstration only
VIN: 4T1BE46K79U123456
Estimate Total: $1850.00
Work: Replace bumper cover, repaint.
"""),
    ("repair-estimate-b.txt", "repair_estimate", """Synthetic repair estimate B — demonstration only
VIN: 4T1BE46K79U654321
Estimate Total: $2275.00
Work: Repair bumper bracket, repaint.
"""),
]


@app.post("/api/v1/demo/seed")
def seed_demo(db: Session = Depends(get_db)):
    """Idempotently load one obviously synthetic case for the local preview."""
    claim = db.scalars(select(Claim).where(Claim.policy_ref == "SYN-DEMO-AUTO-001")).first()
    if claim:
        return claim_view(get_claim(db, claim.id))
    claim = Claim(
        claim_ref="CF-DEMO-001", claimant_label="Alex Example (synthetic)",
        policy_ref="SYN-DEMO-AUTO-001", incident_date="2026-09-18", status="review_required",
    )
    db.add(claim)
    db.flush()
    for filename, kind, body in DEMO_DOCS:
        db.add(Document(
            claim_id=claim.id, filename=filename, document_type=kind,
            text=body, extracted_facts=extract_facts(body),
        ))
    db.add(AuditEvent(
        claim_id=claim.id, action="demo.case_loaded",
        detail={"source": "synthetic_sample", "claim_action": "none"},
    ))
    db.commit()
    db.expire_all()  # Refresh eagerly-loaded relations before serializing.
    return claim_view(get_claim(db, claim.id))
