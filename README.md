# ConflictSense ◈
**Protecting people by exposing hidden enterprise contradictions.**

*Microsoft Agents League 2026 — Reasoning Agents Track*  
*Built solo over 4 days by a second-year engineering student from Mumbai, India.*

---

## 🚀 Live Demo

> [!TIP]
> **Start Here:** The fastest way to understand ConflictSense is to see the 90-second demo.

- **Demo Video (3 Minutes):** [https://youtu.be/kXR18sk17KQ](https://youtu.be/kXR18sk17KQ)
- **Live App:** [https://conflictsense.vercel.app](https://conflictsense.vercel.app)
- **GitHub Repository:** [https://github.com/acchasujal/conflictsense](https://github.com/acchasujal/conflictsense)

---

## ⚡ The Finding That Changes Everything

Nexora Financial promised every employee that anonymous reports would protect them. ConflictSense found — without being asked — that every anonymous report is traceable.

> **Whistleblower Policy §4.2:**  
> *"Employee identity is never logged or traceable by any internal party. The ethics portal does not capture IP addresses, session tokens, device identifiers, or any metadata that could be used to identify the reporter."*

> **IT Security Policy §12.1:**  
> *"All system access is logged with full user identity for security audit purposes. **No exceptions permitted.** Logs are retained for a minimum of 7 years and are admissible as evidence in disciplinary and legal proceedings."*

These two sections cannot simultaneously be true. For the same employee. On the same network. At the same company.

**ConflictSense didn't retrieve this. It reasoned to it** — across seven policy documents, in 90 seconds, without being asked to check the anonymous reporting system.

![The Anonymity Conflict](https://raw.githubusercontent.com/acchasujal/conflictsense/main/judge_screenshots/01_anonymity_conflict_expanded.png)

---

## 🧠 Why This Is Not a Search Engine

A chatbot answers the questions you ask. ConflictSense finds the structural impossibilities you didn't know to ask about.

| What you ask | Standard RAG | ConflictSense |
|---|---|---|
| *"What is the whistleblower policy?"* | Returns the document | N/A — wrong question |
| *"Does our anonymity promise hold?"* | Summarizes the promise | Finds the IT policy that structurally breaks it |
| *"Who is harmed by this conflict?"* | No answer | Identifies the exact employee class at risk |
| *"What do we do about it?"* | No answer | Generates remediation plan gated behind human approval |

---

## ⚙️ Multi-Agent Reasoning Architecture

ConflictSense relies on a multi-stage reasoning pipeline powered by **Azure AI Search**.

![Reasoning Trace Mid-Execution](https://raw.githubusercontent.com/acchasujal/conflictsense/main/judge_screenshots/02_reasoning_trace_mid_execution.png)

1. **PolicyIngestionAgent:** Chunks and indexes policy documents; extracts entities and obligations.
2. **CrossPolicyAnalyzer:** Identifies overlapping entities across document boundaries.
3. **LogicValidator:** Tests whether two obligations can simultaneously hold for the same person.
4. **RiskAssessor:** Classifies the harm by employee category, severity, and human impact.
5. **Human Approval Gate:** No action, no ticket, no remediation without explicit human sign-off.

**Every conflict finding is:**
- Grounded in exact, highlighted citations from the source document.
- Validated by a second agent before surfacing in the UI.
- Gated behind human approval before any governance action.
- Abstained when evidence is insufficient — the system says "I don't know" rather than hallucinating.

![Action Center (Human Approval Gate)](https://raw.githubusercontent.com/acchasujal/conflictsense/main/judge_screenshots/04_action_center.png)

---

## ❤️ Hack for Good: The Human Impact

ConflictSense identifies who is harmed before it identifies what is violated.

![Who Is Harmed (Human Impact)](https://raw.githubusercontent.com/acchasujal/conflictsense/main/judge_screenshots/03_human_impact.png)

- **Whistleblower Retaliation Risk:** Employees who trust anonymous reporting channels are silently exposed when IT audit logging makes anonymity technically impossible. Trust in a protection that doesn't exist is not neutral — it causes people to take risks they would not otherwise accept.
- **Disability Accommodation Barriers:** Employees requiring assistive software or non-standard devices are blocked when HR accommodation policy conflicts with IT's mandatory standard-device policy. 

These are not compliance line-items. These are people.

---

## ♿ Accessibility First

ConflictSense protects marginalized employees. It must be accessible to them.

![Accessibility Demo Active](https://raw.githubusercontent.com/acchasujal/conflictsense/main/judge_screenshots/05_accessibility_active.png)

- **`aria-live="polite"`** on all agent timeline updates — screen readers announce reasoning as it streams.
- **`prefers-reduced-motion` respected** — one toggle disables every animation system-wide.
- **Keyboard navigation throughout** — press `?` to launch the global shortcuts overlay.
- **Full focus trapping** in modal dialogs using native `<dialog>` elements.
- **WCAG AA contrast** on all severity indicators and action buttons.

---

## 🛠️ Microsoft Technology

**Azure AI Search** powers the live upload pipeline:
- Hybrid Retrieval (Keyword + Vector) ensures both semantic and lexical relevance.
- Semantic Ranking surfaces the most policy-relevant passages.
- Every conflict citation is hard-linked to an exact passage from the Azure knowledge base.

---

## 💻 Quickstart

No credentials needed. No build server. Runs in under 30 seconds.

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

---

## 📖 The 90-Second Demo Path

1. Open the [Live App](https://conflictsense.vercel.app).
2. Select **"Whistleblower Anonymity Conflict"** from the scenario dropdown.
3. Click **Run Analysis** — watch the agent timeline fill with real reasoning steps.
4. When the ⚡ unexpected conflict card appears — click it.
5. See **Whistleblower §4.2** highlighted in green. See **IT Security §12.1** highlighted in red.
6. Click **Request Legal Review** — complete the modal, observe the governance ticket injected.
7. Toggle **Accessibility Demo** — navigate the entire experience by keyboard alone.

---

## ℹ️ Disclaimer: All Data Is Synthetic
Every company name, employee, policy, and scenario is 100% fabricated for this submission. Nexora Technologies is fictional. No real PII, no real enterprise data.

## 📜 License
MIT
