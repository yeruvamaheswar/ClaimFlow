"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

type Evidence = {
  document_id: string | null;
  filename: string;
  line: number | null;
  excerpt: string;
  value: string;
};
type Finding = {
  code: string;
  severity: string;
  title: string;
  description: string;
  evidence: Evidence[];
};
type Fact = { value: string; line: number; excerpt: string };
type Document = {
  id: string;
  filename: string;
  document_type: string;
  extracted_facts: Record<string, Fact & { conflicts?: Fact[] }>;
};
type AuditEvent = {
  id: string;
  action: string;
  created_at: string;
  detail: Record<string, unknown>;
};
type Claim = {
  id: string;
  claim_ref: string;
  claimant_label: string;
  policy_ref: string;
  incident_date: string;
  status: string;
  document_count: number;
  finding_count: number;
  documents: Document[];
  findings: Finding[];
  audit_events: AuditEvent[];
};
type ClaimSummary = Pick<
  Claim,
  "id" | "claim_ref" | "claimant_label" | "incident_date" | "status" | "document_count" | "finding_count"
>;

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const DOC_OPTIONS = [
  { value: "claim_form", label: "Claim form" },
  { value: "police_report", label: "Incident report" },
  { value: "repair_estimate", label: "Repair estimate" },
  { value: "policy_excerpt", label: "Policy excerpt" },
  { value: "other", label: "Other" },
];

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    cache: "no-store",
  });
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (typeof body.detail === "string") detail = body.detail;
    } catch { /* Keep status message. */ }
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

function displayDate(date: string): string {
  const d = new Date(`${date}T12:00:00`);
  return Number.isNaN(d.valueOf()) ? date : d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

function statusLabel(status: string): string {
  return status.replaceAll("_", " ");
}

export default function Home() {
  const [claims, setClaims] = useState<ClaimSummary[]>([]);
  const [selected, setSelected] = useState<Claim | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [reviewOpen, setReviewOpen] = useState(false);
  const [docType, setDocType] = useState("other");
  const [docName, setDocName] = useState("note.txt");
  const [docText, setDocText] = useState("");
  const [reviewNote, setReviewNote] = useState("");

  async function reload(focusId?: string) {
    const rows = await request<ClaimSummary[]>("/api/v1/claims");
    setClaims(rows);
    const id = focusId ?? selected?.id ?? rows[0]?.id;
    if (id) setSelected(await request<Claim>(`/api/v1/claims/${id}`));
    else setSelected(null);
  }

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const rows = await request<ClaimSummary[]>("/api/v1/claims");
        if (cancelled) return;
        setClaims(rows);
        if (rows.length > 0) {
          const claim = await request<Claim>(`/api/v1/claims/${rows[0].id}`);
          if (!cancelled) setSelected(claim);
        }
      } catch {
        if (!cancelled) setError("The API isn't reachable. Start the backend at localhost:8000.");
      }
    })();
    return () => { cancelled = true; };
  }, []);

  async function loadDemo() {
    setBusy(true);
    setError(null);
    try {
      const demo = await request<Claim>("/api/v1/demo/seed", { method: "POST" });
      await reload(demo.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load demo.");
    } finally { setBusy(false); }
  }

  async function openClaim(id: string) {
    setError(null);
    try { setSelected(await request<Claim>(`/api/v1/claims/${id}`)); }
    catch (err) { setError(err instanceof Error ? err.message : "Unable to open case."); }
  }

  async function addDocument(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selected) return;
    setBusy(true);
    setError(null);
    try {
      await request(`/api/v1/claims/${selected.id}/documents`, {
        method: "POST", body: JSON.stringify({ filename: docName, document_type: docType, text: docText }),
      });
      setUploadOpen(false);
      setDocText("");
      await reload(selected.id);
    } catch (err) { setError(err instanceof Error ? err.message : "Could not add document."); }
    finally { setBusy(false); }
  }

  async function recordReview(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selected) return;
    setBusy(true);
    setError(null);
    try {
      await request(`/api/v1/claims/${selected.id}/review`, {
        method: "POST", body: JSON.stringify({ note: reviewNote }),
      });
      setReviewOpen(false);
      setReviewNote("");
      await reload(selected.id);
    } catch (err) { setError(err instanceof Error ? err.message : "Could not save review."); }
    finally { setBusy(false); }
  }

  const totalFindings = useMemo(() => claims.reduce((sum, c) => sum + c.finding_count, 0), [claims]);
  const totalDocs = useMemo(() => claims.reduce((sum, c) => sum + c.document_count, 0), [claims]);

  return (
    <div className="shell">
      <aside className="sidebar" aria-label="Primary navigation">
        <div className="brand">
          <div className="brand-mark" aria-hidden="true"><span>CF</span></div>
          <div><div className="brand-name">ClaimFlow</div><div className="brand-caption">Evidence operations</div></div>
        </div>
        <div className="nav-label">WORKSPACE</div>
        <div className="nav-item active"><span className="nav-icon">◫</span> Overview</div>
        <div className="nav-item"><span className="nav-icon">▤</span> Claims <span className="nav-count">{claims.length}</span></div>
        <div className="nav-label nav-label-secondary">ENVIRONMENT</div>
        <div className="sandbox-card">
          <span className="sandbox-dot" /> Synthetic data only
          <p>Read-only decision support. No real claims processing.</p>
        </div>
        <div className="side-footer"><span>CF / 0.1</span><span>Foundations build</span></div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div className="breadcrumbs">WORKSPACE <span>/</span> OVERVIEW</div>
          <div className="topbar-right"><span className="env-tag">DEMO ENVIRONMENT</span><div className="avatar">CF</div></div>
        </header>

        <div className="content">
          <div className="eyebrow">EVIDENCE INTELLIGENCE / V0.1</div>
          <section className="page-title">
            <div>
              <h1>Claims, with clarity.</h1>
              <p>A controlled workspace to review evidence, surface inconsistencies, and keep people in the loop.</p>
            </div>
            <button className="primary-button" onClick={loadDemo} disabled={busy}>
              <span aria-hidden="true">＋</span> {busy ? "Working…" : "Load example claim"}
            </button>
          </section>

          {error && <div className="error" role="alert">{error}</div>}

          <section className="metrics" aria-label="Workspace metrics">
            <div className="metric"><span>CLAIMS IN WORKSPACE</span><strong>{claims.length.toString().padStart(2, "0")}</strong><small>Simulated records</small></div>
            <div className="metric"><span>EVIDENCE DOCUMENTS</span><strong>{totalDocs.toString().padStart(2, "0")}</strong><small>Structured for review</small></div>
            <div className="metric"><span>ITEMS TO REVIEW</span><strong>{totalFindings.toString().padStart(2, "0")}</strong><small>Flagged, not adjudicated</small></div>
          </section>

          <section className="workbench">
            <div className="section-heading"><h2>Review workspace</h2><p>Evidence-backed case examination</p></div>
            <div className="work-grid">
              <div className="case-list">
                <div className="panel-label">CASES <span>{claims.length}</span></div>
                {claims.length === 0 ? (
                  <div className="empty"><div className="empty-icon">▤</div><strong>No claims yet</strong><p>Load an example to explore the evidence workflow.</p><button onClick={loadDemo} disabled={busy}>Load synthetic sample →</button></div>
                ) : claims.map((claim) => (
                  <button key={claim.id} className={`case-row ${selected?.id === claim.id ? "chosen" : ""}`} onClick={() => openClaim(claim.id)}>
                    <span className="case-row-main"><b>{claim.claim_ref}</b><small>{claim.claimant_label}</small><small>Incident · {displayDate(claim.incident_date)}</small></span>
                    <span className="case-row-bottom"><span className="tiny-tag">{statusLabel(claim.status)}</span><span className="finding-chip">{claim.finding_count} flags</span></span>
                  </button>
                ))}
              </div>

              <div className="case-detail">
                {!selected ? <div className="select-empty"><div className="select-empty-art">◇</div><h3>Select a claim to begin</h3><p>Documents, discrepancies, and audit entries will appear here.</p></div> : (
                  <>
                    <div className="detail-header"><div><div className="mini-eyebrow">CASE FILE</div><h3>{selected.claim_ref}</h3><p>{selected.claimant_label} <span>·</span> {selected.policy_ref}</p></div><span className="status-pill">● {statusLabel(selected.status)}</span></div>
                    <div className="detail-stats"><span><b>{selected.document_count}</b> evidence documents</span><span><b>{selected.finding_count}</b> review findings</span><span>Incident <b>{displayDate(selected.incident_date)}</b></span></div>

                    <div className="subsection-header"><h4>Review findings</h4><span>TRACEABLE EVIDENCE</span></div>
                    {selected.findings.length === 0 ? <p className="muted-note">No differences detected by the demonstration checks. Human review is still required.</p> : (
                      <div className="findings-list">
                        {selected.findings.map((finding) => (
                          <article className="finding" key={finding.code}>
                            <div className="finding-head"><span className="attention-mark">!</span><div><h5>{finding.title}</h5><p>{finding.description}</p></div></div>
                            {finding.evidence.length > 0 && <div className="evidence-list">
                              {finding.evidence.map((evidence, index) => (
                                <div className="evidence-line" key={`${evidence.filename}-${index}`}>
                                  <div className="evidence-source">{evidence.filename}{evidence.line ? ` · line ${evidence.line}` : ""}</div>
                                  <code>{evidence.excerpt}</code>
                                </div>
                              ))}
                            </div>}
                          </article>
                        ))}
                      </div>
                    )}

                    <div className="subsection-header documents-heading"><h4>Source documents</h4><button onClick={() => setUploadOpen((open) => !open)}>+ Add text evidence</button></div>
                    <div className="document-list">
                      {selected.documents.length === 0 ? <p className="muted-note">No evidence added yet.</p> : selected.documents.map((doc) => (
                        <div className="document-row" key={doc.id}><span className="doc-icon">TXT</span><div><b>{doc.filename}</b><small>{doc.document_type.replaceAll("_", " ")} · {Object.keys(doc.extracted_facts).length} structured fields</small></div><span className="document-check">✓</span></div>
                      ))}
                    </div>

                    {uploadOpen && <form className="inline-form" onSubmit={addDocument}>
                      <h5>Add synthetic text evidence</h5>
                      <label>Document type<select value={docType} onChange={(e) => setDocType(e.target.value)}>{DOC_OPTIONS.map((opt) => <option key={opt.value} value={opt.value}>{opt.label}</option>)}</select></label>
                      <label>File label<input value={docName} onChange={(e) => setDocName(e.target.value)} minLength={1} maxLength={150} required /></label>
                      <label>Text contents<textarea value={docText} onChange={(e) => setDocText(e.target.value)} placeholder={"Incident Date: 2026-09-18\nVIN: 4T1BE46K79U123456"} rows={4} required /></label>
                      <div className="form-actions"><button type="button" className="text-button" onClick={() => setUploadOpen(false)}>Cancel</button><button className="primary-button" disabled={busy}>Save evidence</button></div>
                    </form>}

                    <div className="subsection-header audit-heading"><h4>Activity trail</h4><span>APPEND-ONLY EVENTS*</span></div>
                    <div className="audit-list">{[...selected.audit_events].reverse().map((event) => <div key={event.id} className="audit-row"><span className="audit-dot" /><div><b>{event.action.replaceAll(".", " · ")}</b><small>{new Date(event.created_at).toLocaleString("en-US")}</small></div></div>)}</div>
                    <div className="review-footer"><p>Review notes do not settle, approve, or deny claims.</p><button className="secondary-button" onClick={() => setReviewOpen((open) => !open)}>Record review note →</button></div>
                    {reviewOpen && <form className="inline-form" onSubmit={recordReview}><label>Review note<textarea value={reviewNote} onChange={(e) => setReviewNote(e.target.value)} minLength={10} maxLength={2000} rows={3} placeholder="Record an observation or necessary follow-up…" required /></label><div className="form-actions"><button type="button" className="text-button" onClick={() => setReviewOpen(false)}>Cancel</button><button className="primary-button" disabled={busy}>Save note</button></div></form>}
                  </>
                )}
              </div>
            </div>
          </section>
          <footer className="footer-note">* Demonstration audit events are application records, not tamper-evident production audit logs. This prototype uses synthetic data only.</footer>
        </div>
      </main>
    </div>
  );
}
