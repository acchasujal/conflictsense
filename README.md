# ConflictSense ◈
**Protecting people by exposing hidden contradictions.**

*Microsoft Agents League 2026 — Reasoning Agents Track*  
*Built solo over 10 days by a final-year engineering student from Mumbai, India.*

---

## The Finding That Changes Everything

Nexora Financial promised every employee that anonymous reports would protect them.

ConflictSense found — without being asked — that every anonymous report is traceable.

> **Whistleblower Policy §4.2:**  
> *"Employee identity is never logged or traceable by any internal party. The ethics portal does not capture IP addresses, session tokens, device identifiers, or any metadata that could be used to identify the reporter."*

> **IT Security Policy §12.1:**  
> *"All system access is logged with full user identity for security audit purposes. **No exceptions permitted.** Logs are retained for a minimum of 7 years and are admissible as evidence in disciplinary and legal proceedings."*

These two sections cannot simultaneously be true. For the same employee. On the same network. At the same company.

**ConflictSense didn't retrieve this. It reasoned to it** — across seven policy documents, in 90 seconds, without being asked to check the anonymous reporting system.

---

## Why This Is Not a Search Engine

| What you ask | Standard RAG | ConflictSense |
|---|---|---|
| "What is the whistleblower policy?" | Returns the document | N/A — wrong question |
| "Does our anonymity promise hold?" | Summarizes the promise | Finds the IT policy that structurally breaks it |
| "Who is harmed by this conflict?" | No answer | Identifies the exact employee class at risk |
| "What do we do about it?" | No answer | Generates remediation plan gated behind human approval |

A chatbot answers the questions you ask. ConflictSense finds the contradictions you didn't know to ask about.

---

## Multi-Agent Reasoning Architecture

```
PolicyIngestionAgent    → chunks and indexes policy documents; extracts entities and obligations
CrossPolicyAnalyzer     → identifies overlapping entities across document boundaries
LogicValidator          → tests whether two obligations can simultaneously hold for the same person
RiskAssessor            → classifies the harm by employee category, severity, and human impact
Human Approval Gate     → no action, no ticket, no remediation without explicit human sign-off
```

**Every conflict finding is:**
- Grounded in exact, highlighted citations from the source document
- Validated by a second agent before surfacing in the UI
- Gated behind human approval before any governance action
- Abstained when evidence is insufficient — the system says "I don't know" rather than hallucinating

The validation chain and the abstention mechanism are what separate this from retrieval. Retrieval returns relevant text. ConflictSense proves that two relevant texts are logically irreconcilable.

---

## Three Modes of Execution

### 1. Verified Demo Scenarios — Offline
Pre-validated reasoning traces from real pipeline runs, replayed deterministically for judging reliability. Zero network dependency. Sub-3-second execution. The output is real — the reasoning pipeline produced it. The playback is engineered for reliability, not to fake reasoning.

**Scenarios included:**
- **Whistleblower Anonymity Conflict** *(primary)* — IT logging makes anonymous reporting impossible
- **Employee Accommodation Conflict** — IT device policy blocks HR-mandated accessibility accommodations
- **Privacy & Data Residency Conflict** — DPDP compliance obligations conflict with US-only infrastructure mandates

### 2. Full Knowledge Base Audit — Offline
Synthetic complete corporate policy library. Generates Executive Dashboard, departmental risk index, and a portfolio of validated conflicts with severity classification.

### 3. Live Upload Analysis — Online · Azure AI Search
Upload custom `.md` policy documents. Azure Hybrid Retrieval (Keyword + Vector) + Semantic Ranking retrieves grounded evidence. Live multi-agent reasoning pipeline. System abstains when evidence is insufficient rather than fabricating findings.

---

## Human Impact

ConflictSense identifies who is harmed before it identifies what is violated.

**Whistleblower Retaliation Risk:** Employees who trust anonymous reporting channels are silently exposed when IT audit logging makes anonymity technically impossible. Trust in a protection that doesn't exist is not neutral — it causes people to take risks they would not otherwise accept.

**Disability Accommodation Barriers:** Employees requiring assistive software or non-standard devices are blocked when HR accommodation policy conflicts with IT's mandatory standard-device policy. The law requires accommodation. The IT policy makes accommodation impossible.

**Employee Privacy Risk:** Data residency requirements conflict with infrastructure jurisdiction mandates, exposing employee data to jurisdictions employees were told it would never reach.

These are not compliance line-items. These are people.

---

## Accessibility

ConflictSense protects marginalized employees. It must be accessible to them.

- **`aria-live="polite"`** on all agent timeline updates — screen readers announce reasoning as it streams, without page reload
- **`prefers-reduced-motion` respected** — one toggle disables every animation system-wide
- **Keyboard navigation throughout** — press `?` to launch the global shortcuts overlay from anywhere
- **Full focus trapping** in modal dialogs using native `<dialog>` elements — no synthetic focus management
- **WCAG AA contrast** on all severity indicators and action buttons
- **Dedicated Accessibility Demo mode** built into the header — not buried in settings

See [docs/accessibility.md](docs/accessibility.md) for full technical documentation.

---

## Microsoft Technology

**Azure AI Search** powers the live upload pipeline:
- Hybrid Retrieval (Keyword + Vector) ensures both semantic and lexical relevance
- Semantic Ranking surfaces the most policy-relevant passages
- Every conflict citation is hard-linked to an exact passage from the Azure knowledge base
- Abstention prevents fabricated citations when retrieval confidence is insufficient

---

## Quickstart

No credentials needed. No build server. Runs in under 30 seconds.

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

**Live deployment:** [conflictsense.vercel.app](https://conflictsense.vercel.app)

---

## The 90-Second Demo Path

1. Open the app at idle state
2. Select **"Whistleblower Anonymity Conflict"** from the scenario dropdown
3. Click **Run Analysis** — watch the agent timeline fill with real reasoning steps and cited passages
4. When the ⚡ unexpected conflict card appears — click it
5. See **Whistleblower §4.2** highlighted in green. See **IT Security §12.1** highlighted in red. Read the proof.
6. Click **Request Legal Review** — complete the modal, observe the governance ticket injected into the timeline
7. Toggle **Accessibility Demo** — navigate the entire experience by keyboard alone

The contradiction is self-evident. No narration required.

---

## All Data Is Synthetic

Every company name, employee, policy, and scenario is 100% fabricated for this submission. Nexora Technologies is fictional. No real PII, no real enterprise data.

---

## Student Context

Built solo over 10 days by Sujal — final-year engineering student, Mumbai, India.  
No team. No prior enterprise compliance background. Free-tier Azure and Vercel throughout.

---

## License
MIT
