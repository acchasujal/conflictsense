# ConflictSense: Complete Project Context for AI Assistants
*Use this document to give Claude or any LLM 100% accurate context. Do not paraphrase the architecture sections.*

---

## 1. The One-Line Pitch
**ConflictSense: Protecting people by exposing hidden enterprise contradictions.**

---

## 2. The Core Story (Use This for the Lead)

Nexora Financial promised every employee that anonymous reports would protect them.

ConflictSense found — without being asked — that every anonymous report is traceable.

**Whistleblower Policy §4.2** says: *"Employee identity is never logged or traceable by any internal party. The ethics portal does not capture IP addresses, session tokens, device identifiers, or any metadata that could be used to identify the reporter."*

**IT Security Policy §12.1** says: *"All system access is logged with full user identity for security audit purposes. No exceptions permitted. Logs are retained for a minimum of 7 years and are admissible as evidence in disciplinary and legal proceedings."*

These two policies cannot simultaneously be true for the same employee on the same network at the same company. ConflictSense proved this — across seven policy documents, in 90 seconds, without being asked to check the anonymous reporting system.

**This is the primary demo moment. The anonymity conflict must lead the video, the submission, and the screenshot plan.**

---

## 3. Why This Is Not RAG (Critical Distinction)

Standard RAG:
- Question: "What does the whistleblower policy say?"
- Answer: Returns the document or a summary of it

ConflictSense:
- No question required
- Task: "Do any obligations in this knowledge base logically contradict each other for the same employee?"
- Answer: "Yes. Here is the proof. Here is who is harmed."

The distinction is logical entailment testing across document boundaries. Retrieval finds text. ConflictSense tests whether two retrieved texts can simultaneously hold as true for the same person.

---

## 4. Technical Architecture (Verified — Use Exactly)

### Frontend
- Pure React (Vite) deployed on Vercel
- Zero backend required for demo scenarios
- Server-Sent Events (SSE) streaming simulation for agent reasoning display

### Multi-Agent Chain (Real — runs live in upload mode)
1. `PolicyIngestionAgent` — chunks documents, extracts entities and obligations
2. `CrossPolicyAnalyzer` — finds entities shared across document boundaries
3. `LogicValidator` — tests whether two obligations can simultaneously hold for the same person; produces a cite-grounded proof
4. `RiskAssessor` — classifies harm: employee category, severity, human impact type
5. `Human Approval Gate` — no governance action without explicit human sign-off

### Azure AI Search (Live in Upload Mode)
- Hybrid Retrieval: Keyword + Vector
- Semantic Ranking for policy relevance
- Every conflict citation hard-linked to an exact passage from the Azure knowledge base
- Abstention when retrieval confidence is insufficient

### Three Execution Modes
1. **Verified Demo Scenarios (Offline):** Pre-validated reasoning traces from real pipeline runs, replayed deterministically. Zero API keys, sub-3-second execution. The precomputed scenarios represent what the live pipeline actually produced.
2. **Full Knowledge Base Audit (Offline):** Synthetic enterprise policy library, executive dashboard, departmental risk index, validated conflict portfolio.
3. **Live Upload Analysis (Online):** Upload `.md` policies, Azure AI Search retrieval, live multi-agent pipeline. Abstains when evidence is insufficient.

---

## 5. Demo Scenarios (All Verified Against Real Policy Text)

### Primary: Whistleblower Anonymity Conflict
- Whistleblower Policy §4.2 guarantees no identity metadata captured
- IT Security Policy §12.1 mandates all system access logged with full user identity, no exceptions
- These two sections are structurally irreconcilable
- Tagged with ⚡ (unexpected finding) — system found it without being asked

### Secondary: Employee Accommodation Conflict
- HR policy: reasonable accommodations required, including specialist assistive software
- IT Security policy: only approved standard-build devices permitted, no exceptions
- An employee requiring accessibility software cannot comply with IT policy while receiving their legally required accommodation

### Tertiary: Privacy / Data Residency Conflict
- DPDP compliance requires India-resident data to remain in-jurisdiction
- IT Security §4.2 mandates all data processing on US-domiciled servers only
- Indian employee data cannot simultaneously comply with both requirements

---

## 6. UI Components (Verified)

- **Reasoning Trace Panel (Left):** Live-streaming agent cards with conclusion text and citations
- **Conflict Dashboard (Right):** Grid of conflict cards with severity badges and ⚡ unexpected-finding badges
- **Conflict Cards:** Expand to show side-by-side contradiction visualization (Policy A vs. Policy B) with exact citation highlighting
- **Status Badges:** Dynamic: NEW → UNDER REVIEW → APPROVED / LEGAL REVIEW / ESCALATED
- **Action Center:** Three buttons per conflict card — Approve Remediation, Request Legal Review, Escalate to Governance Board
- **Modals:** Native HTML5 `<dialog>` with focus trapping, aria-modal, Escape-to-close
- **Toast notifications:** Success feedback on action completion
- **Timeline injection:** Completing a governance action injects a new agent event (GovernanceApprovalAgent, LegalReviewAgent, GovernanceBoardAgent) directly into the reasoning trace

---

## 7. Accessibility Features (All Verified in Code)

- `aria-live="polite"` region in App.jsx — announces each conflict detected and analysis state changes
- `reducedMotion` state disables all CSS animations system-wide when toggled
- `?` key launches keyboard shortcuts overlay from anywhere in the app
- Native `<dialog>` element used for all modals — provides browser-native focus trapping
- WCAG AA contrast on all severity indicators
- Accessibility Demo button in header — activates screen reader mode, reduced motion, and shortcuts overlay simultaneously
- All interactive elements keyboard-navigable via Tab/Enter

---

## 8. Student Context (Include in Submissions)

- **Solo project** — no team members
- **10-day build time** from initial concept to deployment
- **Final-year engineering student** — Mumbai, India
- **No prior enterprise compliance background**
- **Free-tier infrastructure** — Vercel (frontend), Azure Free Tier (AI Search)

---

## 9. Deployment

- **Live:** https://conflictsense.vercel.app
- **GitHub:** https://github.com/acchasujal/conflictsense
- **Local:** `cd frontend && npm install && npm run dev`

---

## 10. What All Data Is

Every company name (Nexora Technologies), every employee, every policy document, and every scenario is 100% synthetic and fabricated for this hackathon. The policy text is written to represent realistic enterprise policy language. No real enterprise data, PII, or confidential materials are present.

---

## 11. Awards Being Targeted

1. **Top Student Award** — Solo student, 10 days, Mumbai, free-tier infrastructure. Highest-probability award.
2. **Hack For Good Award** — Whistleblower protection, disability accommodation rights, privacy. Anonymity conflict is the narrative centerpiece.
3. **Accessibility Award** — Most complete accessibility implementation in the visible field. See docs/accessibility.md.
4. **Best Reasoning Agent** — Multi-agent contradiction detection with abstention and human approval gate. Differentiated from RAG by logical entailment testing across documents.

---

## 12. Priority Instructions for LLMs

When generating scripts, README text, or submission copy using this context:

1. **Lead with the anonymity conflict** — not the accommodation conflict, not generic compliance framing
2. **State the student narrative explicitly** — solo, 10 days, Mumbai, final-year student
3. **Explain the RAG distinction clearly** — ConflictSense tests logical entailment, not retrieval similarity
4. **Do not invent functionality** — do not claim live reasoning during demo scenarios; they are precomputed traces from a validated real run
5. **The abstention mechanism is a feature** — frame it as intellectual honesty, not a limitation
6. **The anonymity conflict is the argument for all four awards** — it is the Reasoning Award story, the Hack For Good story, the Accessibility story, and the Student story simultaneously
