import { useState, useEffect, useRef } from "react";

const DOCUMENTS = [
  { id: 1, name: "IT_Security_Policy.md", dept: "IT Infrastructure", date: "Jan 2024", size: "18 KB" },
  { id: 2, name: "HR_Remote_Work_Policy.md", dept: "Human Resources", date: "Mar 2025", size: "12 KB" },
  { id: 3, name: "Data_Governance_Policy.md", dept: "Legal & Compliance", date: "Nov 2023", size: "22 KB" },
  { id: 4, name: "Employee_Handbook.md", dept: "Human Resources", date: "Feb 2024", size: "41 KB" },
  { id: 5, name: "Whistleblower_Policy.md", dept: "Legal & Compliance", date: "Aug 2023", size: "9 KB" },
  { id: 6, name: "Finance_Expense_Policy.md", dept: "Finance", date: "Jun 2024", size: "14 KB" },
  { id: 7, name: "DPDP_Compliance_Directive.md", dept: "Legal & Compliance", date: "May 2026", size: "7 KB", isNew: true },
];

const TRACE_STEPS = [
  {
    agent: "DocumentAnalyzer",
    agentColor: "#85B7EB",
    time: "0.3s",
    query: "employee data location and processing rules",
    citations: [
      { doc: "IT_Security_Policy.md", section: "§4.2", conf: "high", text: "All company data processing shall occur exclusively on US-domiciled servers. VPN access restricted to US IP ranges." },
      { doc: "HR_Remote_Work_Policy.md", section: "§2.1", conf: "high", text: "Employees may work from any global location without prior approval." },
      { doc: "DPDP_Directive.md", section: "§3.1", conf: "high", text: "Personal data of Indian-resident employees must be processed within Indian jurisdiction. Effective July 1, 2026." },
      { doc: "Data_Governance_Policy.md", section: "§7.3", conf: "medium", text: "EU employee data subject to GDPR residency requirements." },
    ],
    conclusion: null,
  },
  {
    agent: "ConflictDetector",
    agentColor: "#F09595",
    time: "0.8s",
    query: null,
    citations: null,
    conclusion: "IT Security mandates US servers. The DPDP Directive requires Indian servers for Indian-resident employees. HR policy permits those same employees to work from anywhere — which means their data is processed wherever they sit. All three rules apply to the same 34 employees simultaneously. They cannot all be satisfied. This is not ambiguity or edge-case overlap. It is a structural impossibility baked into the current architecture.",
    severity: "CRITICAL",
    confidence: 96,
  },
  {
    agent: "ImpactAssessor",
    agentColor: "#5DCAA5",
    time: "1.1s",
    query: null,
    citations: null,
    conclusion: "34 employees in India-based roles currently fall in the non-compliant zone. Affected systems: primary VPN gateway, US East data pipelines. Affected teams: IT Infrastructure (server provisioning owner), HR (policy amendment owner), Legal (regulatory response). Regulatory deadline: July 1, 2026 — 24 days from today.",
    severity: null,
    confidence: null,
  },
  {
    agent: "RiskQuantifier",
    agentColor: "#FAC775",
    time: "1.4s",
    query: null,
    citations: null,
    conclusion: "Regulatory risk: HIGH. DPDP Act §91 — penalties up to ₹250 crore for systemic non-compliance. Operational risk: MEDIUM — India-region server provisioning requires 2–4 week lead time, which conflicts with the deadline if not started immediately. Legal exposure: HIGH — ongoing violation from July 1 if architecture is unchanged. Reputational risk: MEDIUM — regulatory enforcement actions are public record in India.",
    severity: null,
    confidence: null,
  },
  {
    agent: "DocumentAnalyzer",
    agentColor: "#85B7EB",
    time: "1.9s",
    query: "employee reporting channels and anonymity guarantees",
    citations: [
      { doc: "Whistleblower_Policy.md", section: "§4.2", conf: "high", text: "Reports filed through the ethics portal are anonymous. Employee identity is never logged or traceable by any internal party." },
      { doc: "IT_Security_Policy.md", section: "§12.1", conf: "high", text: "All system access is logged with full user identity for security audit purposes. No exceptions permitted." },
    ],
    conclusion: null,
  },
  {
    agent: "ConflictDetector",
    agentColor: "#F09595",
    time: "2.3s",
    query: null,
    citations: null,
    conclusion: "Nexora's Whistleblower Policy makes a legal commitment to every employee: your report cannot be traced. Its IT Security Policy makes a technical commitment: every system action is logged with user identity, no exceptions. These two statements cannot simultaneously be true. Every report filed through the ethics portal is traceable — full stop. The anonymity guarantee exists on paper. It does not exist in the system.",
    severity: "CRITICAL",
    confidence: 91,
    isSurprise: true,
  },
  {
    agent: "ResolutionRecommender",
    agentColor: "#9FE1CB",
    time: "2.7s",
    query: null,
    citations: null,
    conclusion: "Analysis complete. 9 conflicts detected across 7 policy documents — 3 Critical, 2 High, 4 Medium. Prioritised resolution roadmap generated with owner assignments and deadlines. All findings are pending human review. No autonomous action has been taken or will be taken without explicit approval.",
    severity: null,
    confidence: null,
  },
];

const CONFLICTS = [
  {
    id: 1,
    title: "Data residency: three-way structural impossibility",
    severity: "CRITICAL",
    confidence: 96,
    sources: ["IT_Security_Policy.md §4.2", "HR_Remote_Work_Policy.md §2.1", "DPDP_Directive.md §3.1"],
    affected: "34 India-based employees · IT Infrastructure · Legal",
    deadline: "July 1, 2026 — 24 days",
    resolution: "Option A (recommended): Provision India-region Azure servers — Owner: CTO, Deadline: June 28. Option B: Temporary travel restriction for India-resident staff — Owner: CHRO, Deadline: June 25.",
  },
  {
    id: 2,
    title: "Anonymity guarantee is technically impossible",
    severity: "CRITICAL",
    confidence: 91,
    sources: ["Whistleblower_Policy.md §4.2", "IT_Security_Policy.md §12.1"],
    affected: "All employees · Legal & Compliance · IT Security",
    deadline: null,
    resolution: "Migrate ethics portal to off-system anonymous channel (e.g., third-party hotline) OR carve IT logging exceptions for ethics portal access. Requires Legal + IT Security Director alignment.",
    isSurprise: true,
  },
  {
    id: 3,
    title: "Incident reporting: parallel obligation gap",
    severity: "CRITICAL",
    confidence: 88,
    sources: ["IT_Security_Policy.md §9.1", "Whistleblower_Policy.md §4.2"],
    affected: "All staff · IT Security · Legal · FCA compliance",
    deadline: "FCA 72-hour breach notification window",
    resolution: "Add clause to Whistleblower Policy: security incidents require parallel internal IT Security notification within 2 hours, regardless of external reporting channel used.",
  },
  {
    id: 4,
    title: "BYOD deletion vs. 7-year retention conflict",
    severity: "HIGH",
    confidence: 83,
    sources: ["IT_Security_Policy.md §6.3", "Data_Governance_Policy.md §11.2"],
    affected: "BYOD users · IT · Legal · Compliance",
    deadline: null,
    resolution: "Prohibit storage of sensitive data categories on personal devices — eliminates both obligations simultaneously. Amend IT Security Policy §6.3 with prohibited data type list.",
  },
  {
    id: 5,
    title: "Compensation entitlement: automatic vs. discretionary",
    severity: "HIGH",
    confidence: 79,
    sources: ["Employee_Handbook.md §8.3", "Finance_Expense_Policy.md §5.1"],
    affected: "12 employees currently in qualifying situations · HR · Finance",
    deadline: null,
    resolution: "Amend Handbook §8.3 to require Finance Director pre-approval, OR Finance Policy §5.1 to recognize automatic entitlements. Requires HR and Finance Director alignment.",
  },
  {
    id: 6,
    title: "Software procurement: approval authority gap",
    severity: "MEDIUM",
    confidence: 77,
    sources: ["Finance_Expense_Policy.md §3.1", "IT_Security_Policy.md §11.4"],
    affected: "All departments · IT Security · Finance",
    deadline: null,
    resolution: "Finance Policy must explicitly state IT Security assessment is a prerequisite for all software spend, regardless of value threshold.",
  },
  {
    id: 7,
    title: "Data minimization vs. indefinite retention",
    severity: "MEDIUM",
    confidence: 74,
    sources: ["Data_Governance_Policy.md §3", "Employee_Handbook.md §20"],
    affected: "HR · Legal · All employees",
    deadline: null,
    resolution: "Define a retention schedule with specific periods by data category. Handbook §20 must align with Data Governance minimization principles.",
  },
  {
    id: 8,
    title: "Mandatory MFA vs. contractor exception authority",
    severity: "MEDIUM",
    confidence: 71,
    sources: ["IT_Security_Policy.md §7", "HR_Remote_Work_Policy.md §4"],
    affected: "IT Security · HR · Contractor workforce",
    deadline: null,
    resolution: "Remove manager exception authority from HR Remote Work §4. MFA must be mandatory without exception.",
  },
  {
    id: 9,
    title: "Emergency expenses: receipt vs. self-certification",
    severity: "MEDIUM",
    confidence: 68,
    sources: ["Finance_Expense_Policy.md §8", "Employee_Handbook.md §22"],
    affected: "Finance · All employees",
    deadline: null,
    resolution: "Minor. Align definition of 'emergency expense' across both policies. Handbook §22 threshold should match Finance Policy process.",
  },
];

const SEV = {
  CRITICAL: { color: "#A32D2D", bg: "#FCEBEB", border: "#F09595", dot: "#E24B4A", label: "Critical" },
  HIGH: { color: "#854F0B", bg: "#FAEEDA", border: "#EF9F27", dot: "#BA7517", label: "High" },
  MEDIUM: { color: "#185FA5", bg: "#E6F1FB", border: "#85B7EB", dot: "#378ADD", label: "Medium" },
};

function DocTile({ doc }) {
  return (
    <div style={{
      background: "var(--color-background-primary)",
      border: doc.isNew ? "0.5px solid #85B7EB" : "0.5px solid var(--color-border-tertiary)",
      borderRadius: 8,
      padding: "9px 11px",
      position: "relative",
      transition: "border-color 0.2s",
    }}>
      {doc.isNew && (
        <div style={{ position: "absolute", top: 6, right: 6, background: "#E6F1FB", color: "#0C447C", fontSize: 9, fontWeight: 600, padding: "1px 5px", borderRadius: 3, letterSpacing: "0.4px" }}>NEW</div>
      )}
      <div style={{ fontSize: 10, fontFamily: "monospace", fontWeight: 600, color: "var(--color-text-primary)", marginBottom: 3, paddingRight: doc.isNew ? 28 : 0, wordBreak: "break-all" }}>
        {doc.name}
      </div>
      <div style={{ fontSize: 10, color: "var(--color-text-secondary)" }}>{doc.dept}</div>
      <div style={{ fontSize: 10, color: "var(--color-text-tertiary)", marginTop: 1 }}>Updated {doc.date} · {doc.size}</div>
    </div>
  );
}

function CitationBadge({ src }) {
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 3,
      background: "var(--color-background-secondary)",
      border: "0.5px solid var(--color-border-tertiary)",
      borderRadius: 3, padding: "1px 7px",
      fontSize: 10, fontFamily: "monospace", color: "var(--color-text-secondary)",
    }}>
      <span style={{ opacity: 0.6 }}>📎</span> {src}
    </span>
  );
}

function ConflictCard({ conflict, isSelected, onSelect, onApprove, onReject, isApproved, isRejected }) {
  const sev = SEV[conflict.severity];
  return (
    <div
      onClick={onSelect}
      style={{
        background: "var(--color-background-primary)",
        border: isSelected ? `1px solid ${sev.border}` : "0.5px solid var(--color-border-tertiary)",
        borderLeft: `3px solid ${sev.dot}`,
        borderRadius: 8,
        padding: "10px 12px",
        cursor: "pointer",
        transition: "border 0.15s, box-shadow 0.15s",
        animation: "slideIn 0.3s ease",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4, flexWrap: "wrap" }}>
        <span style={{ background: sev.bg, color: sev.color, fontSize: 10, fontWeight: 600, padding: "1px 6px", borderRadius: 3, letterSpacing: "0.3px", border: `0.5px solid ${sev.border}` }}>
          {sev.label.toUpperCase()}
        </span>
        {conflict.isSurprise && (
          <span style={{ background: "#EEEDFE", color: "#3C3489", fontSize: 10, fontWeight: 500, padding: "1px 6px", borderRadius: 3, border: "0.5px solid #AFA9EC" }}>
            unexpected finding
          </span>
        )}
        {isApproved && <span style={{ background: "#EAF3DE", color: "#27500A", fontSize: 10, fontWeight: 500, padding: "1px 6px", borderRadius: 3 }}>✓ approved</span>}
        {isRejected && <span style={{ background: "var(--color-background-secondary)", color: "var(--color-text-tertiary)", fontSize: 10, padding: "1px 6px", borderRadius: 3 }}>false positive</span>}
        <span style={{ marginLeft: "auto", fontSize: 10, color: "var(--color-text-tertiary)", fontFamily: "monospace" }}>
          {conflict.confidence}% conf
        </span>
      </div>

      <div style={{ fontSize: 13, fontWeight: 500, color: "var(--color-text-primary)", marginBottom: 4, lineHeight: 1.4 }}>
        {conflict.title}
      </div>
      <div style={{ fontSize: 11, color: "var(--color-text-secondary)", marginBottom: 6 }}>
        {conflict.affected}
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
        {conflict.sources.map((src, i) => <CitationBadge key={i} src={src} />)}
      </div>

      {isSelected && (
        <div style={{ marginTop: 10, paddingTop: 10, borderTop: "0.5px solid var(--color-border-tertiary)" }}>
          {conflict.deadline && (
            <div style={{ fontSize: 11, color: "#993C1D", background: "#FAECE7", padding: "4px 10px", borderRadius: 4, marginBottom: 8, display: "inline-block" }}>
              ⏰ {conflict.deadline}
            </div>
          )}
          <div style={{ fontSize: 11, color: "var(--color-text-secondary)", marginBottom: 10, lineHeight: 1.7 }}>
            <span style={{ fontWeight: 500, color: "var(--color-text-primary)" }}>Resolution: </span>
            {conflict.resolution}
          </div>

          {!isApproved && !isRejected ? (
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
              <button onClick={(e) => { e.stopPropagation(); onApprove(); }} style={{ background: "#EAF3DE", color: "#3B6D11", border: "0.5px solid #97C459", borderRadius: 5, padding: "5px 12px", fontSize: 11, fontWeight: 500, cursor: "pointer" }}>
                ✓ Approve finding
              </button>
              <button onClick={(e) => { e.stopPropagation(); onReject(); }} style={{ background: "var(--color-background-secondary)", color: "var(--color-text-secondary)", border: "0.5px solid var(--color-border-secondary)", borderRadius: 5, padding: "5px 12px", fontSize: 11, cursor: "pointer" }}>
                Mark false positive
              </button>
              <button onClick={(e) => e.stopPropagation()} style={{ background: "#E6F1FB", color: "#0C447C", border: "0.5px solid #85B7EB", borderRadius: 5, padding: "5px 12px", fontSize: 11, cursor: "pointer" }}>
                Escalate to legal ↗
              </button>
            </div>
          ) : isApproved ? (
            <div style={{ fontSize: 11, color: "#27500A", background: "#EAF3DE", border: "0.5px solid #97C459", padding: "5px 12px", borderRadius: 5, display: "inline-block" }}>
              ✓ Finding approved — entering resolution workflow
            </div>
          ) : (
            <div style={{ fontSize: 11, color: "var(--color-text-tertiary)", background: "var(--color-background-secondary)", padding: "5px 12px", borderRadius: 5, display: "inline-block" }}>
              Marked as false positive
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function TraceStep({ step, visible }) {
  if (!visible) return null;
  return (
    <div style={{ marginBottom: 14, animation: "fadeInUp 0.35s ease" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 5 }}>
        <span style={{ color: "rgba(255,255,255,0.3)", fontSize: 10, fontFamily: "monospace" }}>[{step.time}]</span>
        <span style={{ color: step.agentColor, fontWeight: 700, fontSize: 11, fontFamily: "monospace" }}>
          {step.agent}
        </span>
        {step.query && (
          <span style={{ color: "rgba(255,255,255,0.35)", fontSize: 10, fontFamily: "monospace" }}>
            → querying: "{step.query}"
          </span>
        )}
      </div>

      {step.citations && step.citations.map((c, i) => (
        <div key={i} style={{ marginLeft: 14, marginBottom: 5 }}>
          <div style={{ color: "#FAC775", fontSize: 10, fontFamily: "monospace" }}>
            ┌ {c.doc} {c.section} <span style={{ color: "rgba(255,255,255,0.25)" }}>[Foundry IQ · {c.conf} confidence]</span>
          </div>
          <div style={{ color: "rgba(255,255,255,0.5)", marginLeft: 10, fontSize: 10, fontFamily: "monospace", fontStyle: "italic" }}>
            └ "{c.text.length > 85 ? c.text.slice(0, 85) + "…" : c.text}"
          </div>
        </div>
      ))}

      {step.conclusion && (
        <div style={{ marginLeft: 14 }}>
          {step.severity && (
            <div style={{
              fontFamily: "monospace",
              fontSize: 10,
              fontWeight: 700,
              marginBottom: 4,
              color: step.severity === "CRITICAL" ? "#F09595" : "#FAC775",
              letterSpacing: "0.3px",
            }}>
              → {step.isSurprise ? "UNEXPECTED " : ""}CONFLICT DETECTED [{step.severity}] — {step.confidence}% confidence
            </div>
          )}
          <div style={{
            color: "rgba(255,255,255,0.72)",
            fontSize: 11,
            lineHeight: 1.85,
            fontFamily: "monospace",
            background: step.isSurprise ? "rgba(242,102,102,0.07)" : "rgba(255,255,255,0.04)",
            padding: "8px 10px",
            borderRadius: 4,
            borderLeft: step.isSurprise ? "2px solid #F09595" : step.severity === "CRITICAL" ? "2px solid rgba(242,75,74,0.4)" : "2px solid rgba(255,255,255,0.1)",
          }}>
            {step.conclusion}
          </div>
        </div>
      )}
    </div>
  );
}

export default function ConflictSense() {
  const [phase, setPhase] = useState("idle");
  const [traceStep, setTraceStep] = useState(-1);
  const [visibleConflicts, setVisibleConflicts] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [approvedIds, setApprovedIds] = useState(new Set());
  const [rejectedIds, setRejectedIds] = useState(new Set());
  const traceRef = useRef(null);

  function runAnalysis() {
    setPhase("scanning");
    setTraceStep(-1);
    setVisibleConflicts([]);
    setApprovedIds(new Set());
    setRejectedIds(new Set());
    setSelectedId(null);

    TRACE_STEPS.forEach((_, i) => {
      setTimeout(() => {
        setTraceStep(i);
        if (traceRef.current) traceRef.current.scrollTop = traceRef.current.scrollHeight;
        if (i === 1) setVisibleConflicts([CONFLICTS[0]]);
        if (i === 5) setVisibleConflicts(c => [...c, CONFLICTS[1], CONFLICTS[2]]);
        if (i === 6) {
          setVisibleConflicts(CONFLICTS);
          setPhase("done");
        }
      }, i * 950 + 500);
    });
  }

  const crit = visibleConflicts.filter(c => c.severity === "CRITICAL").length;
  const high = visibleConflicts.filter(c => c.severity === "HIGH").length;
  const med = visibleConflicts.filter(c => c.severity === "MEDIUM").length;

  return (
    <div style={{ fontFamily: "var(--font-sans, system-ui, sans-serif)", background: "var(--color-background-tertiary)", minHeight: 700 }}>
      <style>{`
        @keyframes fadeInUp { from { opacity:0; transform:translateY(5px); } to { opacity:1; transform:translateY(0); } }
        @keyframes slideIn { from { opacity:0; transform:translateY(4px); } to { opacity:1; transform:translateY(0); } }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }
        .run-btn:hover { filter: brightness(1.1); }
        .run-btn:active { transform: scale(0.98); }
      `}</style>

      {/* Header */}
      <div style={{ background: "var(--color-background-primary)", borderBottom: "0.5px solid var(--color-border-tertiary)", padding: "10px 16px", display: "flex", alignItems: "center", gap: 12 }}>
        <div>
          <div style={{ fontSize: 15, fontWeight: 600, letterSpacing: "-0.3px", color: "var(--color-text-primary)", display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{ color: "#185FA5" }}>◈</span> ConflictSense
          </div>
          <div style={{ fontSize: 10, color: "var(--color-text-tertiary)" }}>Knowledge Conflict Intelligence · Nexora Financial Services</div>
        </div>

        {phase !== "idle" && (
          <div style={{ display: "flex", gap: 6, marginLeft: 8 }}>
            {crit > 0 && <span style={{ background: SEV.CRITICAL.bg, color: SEV.CRITICAL.color, border: `0.5px solid ${SEV.CRITICAL.border}`, padding: "2px 8px", borderRadius: 4, fontSize: 11, fontWeight: 600 }}>{crit} Critical</span>}
            {high > 0 && <span style={{ background: SEV.HIGH.bg, color: SEV.HIGH.color, border: `0.5px solid ${SEV.HIGH.border}`, padding: "2px 8px", borderRadius: 4, fontSize: 11, fontWeight: 600 }}>{high} High</span>}
            {med > 0 && <span style={{ background: SEV.MEDIUM.bg, color: SEV.MEDIUM.color, border: `0.5px solid ${SEV.MEDIUM.border}`, padding: "2px 8px", borderRadius: 4, fontSize: 11, fontWeight: 600 }}>{med} Medium</span>}
          </div>
        )}

        <button
          className="run-btn"
          onClick={runAnalysis}
          disabled={phase === "scanning"}
          style={{
            marginLeft: "auto",
            background: phase === "scanning" ? "var(--color-background-secondary)" : "#185FA5",
            color: phase === "scanning" ? "var(--color-text-tertiary)" : "#fff",
            border: "none",
            borderRadius: 6,
            padding: "7px 16px",
            fontSize: 12,
            fontWeight: 500,
            cursor: phase === "scanning" ? "not-allowed" : "pointer",
            transition: "all 0.2s",
            display: "flex", alignItems: "center", gap: 6,
          }}
        >
          {phase === "scanning" && (
            <span style={{ width: 7, height: 7, borderRadius: "50%", background: "#85B7EB", display: "inline-block", animation: "pulse 1s infinite" }} />
          )}
          {phase === "scanning" ? "Analyzing…" : phase === "done" ? "Re-run Analysis" : "Run Analysis"}
        </button>
      </div>

      {/* Responsible AI banner */}
      <div style={{ background: "#FAEEDA", borderBottom: "0.5px solid #EF9F27", padding: "5px 16px", fontSize: 10, color: "#633806", display: "flex", alignItems: "center", gap: 6 }}>
        <span>⚠</span>
        <span>ConflictSense uses AI to identify potential policy conflicts. All findings require human review before action. This tool does not constitute legal advice.</span>
      </div>

      {/* Two-panel layout */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 340px", minHeight: 620 }}>

        {/* Left: docs + conflicts */}
        <div style={{ padding: "14px 14px 14px 16px", display: "flex", flexDirection: "column", gap: 14, overflow: "auto" }}>
          
          {/* Doc grid */}
          <div>
            <div style={{ fontSize: 10, fontWeight: 500, color: "var(--color-text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 7 }}>
              Document corpus — {DOCUMENTS.length} policies
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(148px, 1fr))", gap: 6 }}>
              {DOCUMENTS.map(doc => <DocTile key={doc.id} doc={doc} />)}
            </div>
          </div>

          {/* Idle CTA */}
          {phase === "idle" && (
            <div style={{ textAlign: "center", padding: "40px 20px", color: "var(--color-text-tertiary)", borderRadius: 10, border: "0.5px dashed var(--color-border-tertiary)" }}>
              <div style={{ fontSize: 28, marginBottom: 10 }}>🔍</div>
              <div style={{ fontSize: 13, fontWeight: 500, color: "var(--color-text-secondary)", marginBottom: 6 }}>
                7 policy documents loaded
              </div>
              <div style={{ fontSize: 12, maxWidth: 320, margin: "0 auto", lineHeight: 1.7, color: "var(--color-text-tertiary)" }}>
                ConflictSense will interrogate each document simultaneously, comparing what they say about the same topics — and listening to how they disagree.
              </div>
              <div style={{ marginTop: 14, fontSize: 11, color: "#854F0B", background: "#FAEEDA", border: "0.5px solid #FAC775", padding: "6px 14px", borderRadius: 6, display: "inline-block" }}>
                ⏰ DPDP compliance deadline: July 1, 2026 — 24 days
              </div>
            </div>
          )}

          {/* Conflicts */}
          {visibleConflicts.length > 0 && (
            <div>
              <div style={{ fontSize: 10, fontWeight: 500, color: "var(--color-text-tertiary)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 7 }}>
                Conflicts detected — {visibleConflicts.length} of {phase === "done" ? CONFLICTS.length : "…"} — click to review
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                {visibleConflicts.map(c => (
                  <ConflictCard
                    key={c.id}
                    conflict={c}
                    isSelected={selectedId === c.id}
                    onSelect={() => setSelectedId(selectedId === c.id ? null : c.id)}
                    onApprove={() => setApprovedIds(prev => new Set([...prev, c.id]))}
                    onReject={() => setRejectedIds(prev => new Set([...prev, c.id]))}
                    isApproved={approvedIds.has(c.id)}
                    isRejected={rejectedIds.has(c.id)}
                  />
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right: Trace panel */}
        <div style={{ borderLeft: "0.5px solid var(--color-border-tertiary)", background: "#18181B", display: "flex", flexDirection: "column", overflow: "hidden" }}>
          
          {/* Trace header */}
          <div style={{ padding: "10px 14px", borderBottom: "0.5px solid rgba(255,255,255,0.07)", display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{
              width: 7, height: 7, borderRadius: "50%",
              background: phase === "scanning" ? "#EF9F27" : phase === "done" ? "#639922" : "#444441",
              transition: "background 0.4s",
              animation: phase === "scanning" ? "pulse 1s infinite" : "none",
            }} />
            <span style={{ fontFamily: "monospace", fontSize: 10, fontWeight: 600, color: "rgba(255,255,255,0.45)", letterSpacing: "0.5px" }}>
              REASONING TRACE
            </span>
            {phase === "done" && (
              <span style={{ marginLeft: "auto", fontFamily: "monospace", fontSize: 10, color: "#97C459" }}>✓ COMPLETE</span>
            )}
            {phase === "scanning" && (
              <span style={{ marginLeft: "auto", fontFamily: "monospace", fontSize: 10, color: "#EF9F27" }}>● RUNNING</span>
            )}
          </div>

          {/* Trace body */}
          <div ref={traceRef} style={{ flex: 1, overflow: "auto", padding: "12px 14px" }}>
            {phase === "idle" && (
              <div style={{ textAlign: "center", paddingTop: 40, fontFamily: "monospace", fontSize: 11, color: "rgba(255,255,255,0.18)" }}>
                reasoning trace will appear here<br />during analysis
              </div>
            )}

            {TRACE_STEPS.map((step, i) => (
              <div key={i}>
                <TraceStep step={step} visible={i <= traceStep} />
                {i <= traceStep && i < TRACE_STEPS.length - 1 && (
                  <div style={{ borderTop: "0.5px solid rgba(255,255,255,0.05)", marginBottom: 12 }} />
                )}
              </div>
            ))}

            {phase === "done" && (
              <div style={{ marginTop: 10, padding: "8px 10px", background: "rgba(99,153,34,0.1)", borderRadius: 4, borderLeft: "2px solid #639922", animation: "fadeInUp 0.3s ease" }}>
                <span style={{ fontFamily: "monospace", color: "#97C459", fontSize: 10 }}>
                  analysis complete · 9 conflicts · all pending human review · no autonomous action taken
                </span>
              </div>
            )}
          </div>

          {/* Foundry IQ attribution */}
          <div style={{ padding: "8px 14px", borderTop: "0.5px solid rgba(255,255,255,0.07)", display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{ fontFamily: "monospace", fontSize: 9, color: "rgba(255,255,255,0.25)" }}>powered by</span>
            <span style={{ fontFamily: "monospace", fontSize: 9, fontWeight: 700, color: "#378ADD" }}>Azure Foundry IQ</span>
            <span style={{ fontFamily: "monospace", fontSize: 9, color: "rgba(255,255,255,0.2)" }}>· every citation grounded · auditable</span>
          </div>
        </div>
      </div>
    </div>
  );
}
