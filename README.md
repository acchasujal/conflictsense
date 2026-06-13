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

![The Anonymity Conflict](docs/images/Anonymity%20Conflict.png)

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

ConflictSense relies on a disciplined, multi-stage reasoning pipeline designed to prioritize logical entailment and human safety over simple text retrieval. It operates through specialized agents managed by a central Orchestrator.

```mermaid
graph TD
    %% Styling
    classDef user fill:#2C3E50,stroke:#none,color:#fff,font-weight:bold,padding:10px
    classDef retrieve fill:#2980B9,stroke:#none,color:#fff,font-weight:bold,padding:10px
    classDef reason fill:#8E44AD,stroke:#none,color:#fff,font-weight:bold,padding:10px
    classDef validate fill:#E67E22,stroke:#none,color:#fff,font-weight:bold,padding:10px
    classDef govern fill:#C0392B,stroke:#none,color:#fff,font-weight:bold,padding:10px

    %% Layers
    INPUT["User Input / Policy Upload"]:::user
    
    subgraph Retrieval Layer
        DA["DocumentAnalyzer<br/>(Azure AI Search: Hybrid + Semantic)"]:::retrieve
    end
    
    subgraph Reasoning Layer
        CD["ConflictDetector<br/>(Logical Entailment Testing)"]:::reason
    end
    
    subgraph Validation Layer
        VAL["ConflictValidatorAgent<br/>(Abstention / Grounding Check)"]:::validate
    end
    
    subgraph Risk Layer
        IA["ImpactAssessor & RiskQuantifier<br/>(Harm Classification)"]:::validate
    end

    subgraph Governance Layer
        RR["ResolutionRecommender"]:::govern
        GATE["Human Approval Gate<br/>(Action Center UI)"]:::govern
    end

    %% Flow
    INPUT --> DA
    DA --> CD
    CD --> VAL
    
    VAL -- "Insufficient Evidence" --> ABSTAIN["System Abstains (No Hallucination)"]
    VAL -- "Validated Proof" --> IA
    
    IA --> RR
    RR --> GATE
```

![Reasoning Trace Mid-Execution](docs/images/Reasoning%20Trace%20Mid-Execution.png)

**1. Retrieval & Grounding Layer (`DocumentAnalyzer`)**
When a policy enters the system, it is indexed into **Azure AI Search**. The analyzer uses Hybrid Retrieval (Keyword + Vector) and Semantic Ranking to surface highly relevant chunks.

**2. Logical Entailment Layer (`ConflictDetector`)**
This is what separates ConflictSense from a retrieval chatbot. The detector tests whether two obligations can simultaneously hold for the same employee class. It does not summarize; it proves structural impossibilities. 

**3. Validation & Abstention Layer (`ConflictValidatorAgent`)**
A secondary agent acts as an adversarial reviewer. If a candidate conflict lacks citations from at least two *distinct* documents, or if confidence falls below the strict 65% threshold, the system **abstains**. It outputs "Insufficient validated evidence" rather than hallucinating a finding.

**4. Risk & Impact Layer (`ImpactAssessor` & `RiskQuantifier`)**
Operating in parallel, these agents shift focus from *what is violated* to *who is harmed*. They classify the employee category at risk (e.g., Whistleblower, Disabled Employee) and assign a severity score.

**5. Governance Layer (`ResolutionRecommender` & `Human Approval Gate`)**
The system proposes a remediation plan, but takes zero automated action. Every generated ticket or policy block is intercepted by a strict Human Approval Gate in the UI, requiring explicit human sign-off before routing to Legal or HR.

**The Reliability Fallback Chain (4-Tier Architecture):**
To guarantee zero cold-start failures during judging:
- **Tier 1:** Live Azure AI Search + Primary LLM (Groq via OpenRouter/Native API).
- **Tier 2:** Automatic LLM Provider Failover (routes to Nvidia if Primary fails).
- **Tier 3:** Precomputed Trace Replay (Offline, verified demo scenarios).
- **Tier 4:** Hard Abstention.

![Action Center (Human Approval Gate)](docs/images/Human%20Approval%20Gate.png)

---

## ❤️ Hack for Good: The Human Impact

ConflictSense identifies who is harmed before it identifies what is violated.

![Who Is Harmed (Human Impact)](docs/images/Human%20Impact%20section.png)

- **Whistleblower Retaliation Risk:** Employees who trust anonymous reporting channels are silently exposed when IT audit logging makes anonymity technically impossible. Trust in a protection that doesn't exist is not neutral — it causes people to take risks they would not otherwise accept.
- **Disability Accommodation Barriers:** Employees requiring assistive software or non-standard devices are blocked when HR accommodation policy conflicts with IT's mandatory standard-device policy. 

These are not compliance line-items. These are people.

---

## ♿ Accessibility First

ConflictSense protects marginalized employees. It must be accessible to them.

![Accessibility Demo Active](docs/images/Accessibility%20Demo.png)

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
