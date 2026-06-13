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

**This is what distinguishes ConflictSense from standard retrieval systems.**

A standard RAG system answers the questions you ask. ConflictSense finds the structural impossibilities between policies that neither document acknowledges — but that employees live with every day.

A whistleblower who trusts an anonymity guarantee that doesn't technically exist is not just exposed. They made a decision under false information that no system flagged before ConflictSense.

---

## Microsoft Technology

**Azure AI Search** powers the live upload analysis pipeline:

- **Hybrid Retrieval (Keyword + Vector):** Ensures both semantic and lexical relevance for policy documents.
- **Semantic Ranking:** Surfaces the most policy-critical passages to feed the reasoning agents.
- **Grounding & Abstention:** Every conflict citation is hard-linked to an exact passage retrieved from the Azure knowledge base. The system abstains when retrieval confidence is insufficient — zero fabricated citations.

The upload pipeline accepts custom Markdown policy documents, indexes them via Azure AI Search, and runs a live multi-agent reasoning chain to detect novel contradictions the authors never anticipated.

---

## Reasoning Agent Architecture

ConflictSense is explicitly a **reasoning agent**, not a retrieval agent. It tests logical entailment across documents.

**Five agents partition the reasoning workload:**

1. `PolicyIngestionAgent` — chunks documents, extracts entities and obligations.
2. `CrossPolicyAnalyzer` — finds entities shared across document boundaries and identifies the logical relation between their associated obligations.
3. `LogicValidator` — tests whether two obligations can simultaneously hold for the same employee class; produces a cite-grounded proof.
4. `RiskAssessor` — classifies harm by employee category, severity level, and human impact type.
5. `Human Approval Gate` — no governance action without explicit human sign-off.

**Why this is Reasoning and not Retrieval:**
Retrieval answers: *"What does Policy A say?"*  
Reasoning answers: *"Can Policy A and Policy B simultaneously hold for the same employee at the same company?"*  

This is not a different prompt. It is a completely different computational task. The **abstention mechanism** is the strongest signal of architectural discipline: when evidence is insufficient to prove a contradiction with confidence, the system says so explicitly and routes to human review rather than hallucinating a finding.

---

## Accessibility

ConflictSense protects marginalized employees. The tool itself must be accessible to them.

- **Screen Reader First:** `aria-live="polite"` on all agent timeline updates ensures screen readers announce reasoning as it streams dynamically. Dedicated Screen Reader Mode provides real-time ARIA announcements for every conflict detected and every agent step completed.
- **Motion Control:** `prefers-reduced-motion` is fully respected — one toggle disables all animations system-wide.
- **Keyboard Navigation:** Fully navigable without a mouse. Press `?` to launch a global shortcuts overlay.
- **Focus Management:** Full focus trapping in modal dialogs via native `<dialog>` elements ensures keyboard users are never lost.
- **Visual Contrast:** WCAG AA contrast on all severity indicators and action buttons.
- **Built-In Visibility:** A dedicated Accessibility Demo mode is prominently featured in the header — not an afterthought buried in settings.

The employee who most needs ConflictSense's protection is the one filing a report under a policy that secretly doesn't protect them. That employee must be able to use this tool seamlessly.

---

## Hack for Good: The Human Impact

ConflictSense is built on a simple premise: identify *who is harmed* before identifying *what is violated*. 

- **Whistleblower Retaliation Risk:** Employees who trust anonymous reporting channels are silently exposed when IT audit logging makes anonymity technically impossible. Trust in a broken protection causes people to take risks they would not otherwise accept.
- **Disability Accommodation Barriers:** Employees requiring assistive software or non-standard devices are blocked when HR accommodation policy conflicts with IT's mandatory standard-device mandate. The law requires accommodation. The IT policy makes accommodation technically impossible.
- **Employee Privacy Risk:** Data residency requirements conflict with infrastructure jurisdiction mandates, exposing employee data to jurisdictions employees were told it would never reach.

These are not abstract compliance issues. These are structural failures that directly harm people. ConflictSense protects employees by surfacing these impossibilities before they cause harm.

---

## What Makes ConflictSense Different

| Feature | Standard RAG | ConflictSense |
|---|---|---|
| **Core Task** | Retrieve relevant documents | Detect logical impossibilities between documents |
| **Output** | Passages about a topic | Proof that two obligations cannot coexist |
| **Human Impact** | Not assessed | Primary output: who is harmed |
| **Confidence** | Similarity score | Validation agent + deliberate abstention |
| **Governance** | None | Human approval gate on every action |
| **Failure Mode**| Returns low-relevance text | Abstains and routes to human review |

---

## Deployment

**Live Demo App:** [conflictsense.vercel.app](https://conflictsense.vercel.app)  
**GitHub Repo:** [github.com/acchasujal/conflictsense](https://github.com/acchasujal/conflictsense)  
**Run locally:** `cd frontend && npm install && npm run dev`

No credentials required for the 90-second verified demo scenarios.

---

## Student Context

Built solo over 10 days by Sujal — final-year engineering student, Mumbai, India.  
No team. No prior enterprise compliance background. Deployed on free-tier Azure and Vercel infrastructure throughout. Built with a passion for using AI to protect vulnerable populations.

---

## Data Notice

All company names, employees, policies, and scenarios are 100% synthetic and fabricated for this submission. There is no real enterprise data, PII, or confidential materials in this repository.
