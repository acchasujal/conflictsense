# ConflictSense — Ultimate Submission Package

---

## Title
**ConflictSense**

## Tagline
Protecting people by exposing hidden enterprise contradictions.

---

## Submission Description

Nexora promised every employee that anonymous reports would protect them.

ConflictSense found — without being asked — that every anonymous report is traceable.

Whistleblower Policy §4.2 guarantees that employee identity is never logged, that no IP addresses or session tokens are captured, and that no metadata could identify a reporter. IT Security Policy §12.1 mandates that all system access is logged with full user identity, no exceptions, retained for seven years, admissible as evidence.

These two policies cannot simultaneously be true. ConflictSense proved it — across seven documents, in 90 seconds, without being prompted to inspect the anonymous reporting system.

---

**This is what distinguishes ConflictSense from retrieval systems.**

A standard RAG system answers the questions you ask. ConflictSense finds the structural impossibilities between policies that neither document acknowledges — but that employees live with every day.

A whistleblower who trusts an anonymity guarantee that doesn't technically exist is not just exposed. They made a decision under false information that no system flagged before ConflictSense.

---

## Microsoft Technology

**Azure AI Search** powers the live upload analysis pipeline:

- Hybrid Retrieval (Keyword + Vector) ensures both semantic and lexical relevance
- Semantic Ranking surfaces the most policy-critical passages
- Every conflict citation is hard-linked to an exact passage retrieved from the Azure knowledge base
- The system abstains when retrieval confidence is insufficient — no fabricated citations

The upload pipeline accepts custom Markdown policy documents, indexes them via Azure AI Search, and runs a live multi-agent reasoning chain to detect novel contradictions the authors never anticipated.

---

## Reasoning Agent Architecture

ConflictSense is explicitly a reasoning agent, not a retrieval agent.

**Five agents partition the reasoning workload:**

1. `PolicyIngestionAgent` — chunks documents, extracts entities and obligations
2. `CrossPolicyAnalyzer` — finds entities shared across document boundaries and identifies the logical relation between their associated obligations
3. `LogicValidator` — tests whether two obligations can simultaneously hold for the same employee class; produces a cite-grounded proof
4. `RiskAssessor` — classifies harm by employee category, severity level, and human impact type
5. `Human Approval Gate` — no governance action without explicit human sign-off

**What makes this reasoning and not retrieval:**

Retrieval answers: "What does Policy A say?"  
Reasoning answers: "Can Policy A and Policy B simultaneously hold for the same employee at the same company?"  

The distinction is logical entailment testing across documents. This is not a different prompt. It is a different computational task.

**The abstention mechanism** is the strongest signal of architectural discipline: when evidence is insufficient to prove a contradiction with confidence, the system says so explicitly and routes to human review rather than fabricating a finding.

---

## Accessibility

ConflictSense protects marginalized employees. It must be accessible to them.

- `aria-live="polite"` on all agent timeline updates — screen readers announce reasoning as it streams
- `prefers-reduced-motion` fully respected — one toggle disables all animations
- Keyboard navigation throughout — `?` launches global shortcuts overlay
- Full focus trapping in modal dialogs via native `<dialog>` elements
- WCAG AA contrast on all severity indicators and action buttons
- Dedicated Accessibility Demo mode in the header — not a settings page afterthought
- Screen Reader Mode: real-time ARIA announcements for every conflict detected and every agent step completed

The employee who most needs ConflictSense's protection is the one filing a report under a policy that secretly doesn't protect them. That employee must be able to use this tool.

---

## Human Impact

ConflictSense identifies who is harmed before it identifies what is violated.

**Whistleblower Retaliation Risk:** Employees who trust anonymous reporting channels are silently exposed when IT audit logging makes anonymity technically impossible. Trust in a broken protection causes people to take risks they would not otherwise accept.

**Disability Accommodation Barriers:** Employees requiring assistive software or non-standard devices are blocked when HR accommodation policy conflicts with IT's mandatory standard-device mandate. The law requires accommodation. The IT policy makes accommodation technically impossible.

**Employee Privacy Risk:** Data residency requirements conflict with infrastructure jurisdiction mandates, exposing employee data to jurisdictions employees were told it would never reach.

---

## What Makes ConflictSense Different

| | Standard RAG | ConflictSense |
|---|---|---|
| Task | Retrieve relevant documents | Detect logical impossibilities between documents |
| Output | Passages about a topic | Proof that two obligations cannot coexist |
| Human impact | Not assessed | Primary output: who is harmed |
| Confidence mechanism | Similarity score | Validation agent + abstention |
| Governance | None | Human approval gate on every action |
| Failure mode | Returns low-relevance text | Abstains and routes to human review |

---

## Deployment

**Live:** https://conflictsense.vercel.app  
**GitHub:** https://github.com/acchasujal/conflictsense  
**Run locally:** `cd frontend && npm install && npm run dev`

No credentials required for the demo scenarios.

---

## Student Context

Built solo over 10 days by Sujal — final-year engineering student, Mumbai, India.  
No team. No prior enterprise compliance background. Free-tier Azure and Vercel infrastructure throughout.

---

## Data

All company names, employees, policies, and scenarios are 100% synthetic and fabricated for this submission. No real enterprise data, PII, or confidential materials.
