# ConflictSense Demo Script

**Company Context:** Nexora Financial Services, a mid-sized multinational fintech facing an upcoming DPDP compliance audit.
**Core Wow Moment:** Uncovering that the company's "anonymous" whistleblower policy is actually mathematically impossible to keep anonymous due to aggressive IT security logging.

---

## 90-Second "Elevator Pitch" Script

**(0:00 - 0:15) The Problem**
*"Hi judges! We built ConflictSense. At Nexora Financial Services, we have dozens of enterprise policies—HR, IT, Legal. They are written by different teams, updated at different times. No human can hold all of them in their head at once, which leads to hidden, catastrophic compliance risks."*

**(0:15 - 0:45) The Demo & Wow Moment**
*(Click "Run Analysis")*
*"Watch the Reasoning Trace on the right. ConflictSense uses a multi-agent architecture powered by Azure AI Search to read, understand, and cross-reference every policy simultaneously.
Look at this critical finding! The Whistleblower Policy guarantees complete anonymity. But ConflictSense just found that our IT Security Policy mandates full user identity logging for all network traffic with 'no exceptions permitted'.
It is mathematically impossible to report anonymously at Nexora. A human auditor would take weeks to find this contradiction across 50-page documents. ConflictSense found it in seconds."*

**(0:45 - 1:30) The Value Proposition**
*(Click on the Conflict Card to expand it)*
*"Notice how every claim is grounded with exact citations and confidence scores. From here, a compliance officer can instantly escalate this to legal or approve an AI-generated remediation workflow. ConflictSense doesn't just read documents; it reasons about the gaps between them to save enterprises from massive compliance fines. Thank you!"*

---

## 5-Minute "Deep Dive" Script

**(0:00 - 1:00) Context & Architecture**
- Introduce Nexora Financial Services.
- Explain the pain point: Siloed policy writing leads to contradictions.
- Highlight the tech stack: A multi-agent system (`DocumentAnalyzer`, `ConflictDetector`, `ImpactAssessor`, `RiskQuantifier`, `ResolutionRecommender`) orchestrated locally, but utilizing **Azure AI Search** for semantic hybrid retrieval and **Foundry IQ** for grounded citations.

**(1:00 - 2:30) The Live Analysis**
- Click **"Run Analysis"**.
- Draw attention to the **Reasoning Trace (Right Panel)**. Point out that this isn't just a single LLM call; it's a pipeline of specialized agents debating each other.
- Emphasize the live streaming nature of the trace. Mention that the UI is fully accessible (WCAG 2.1 compliant), utilizing `aria-live` regions so screen readers can follow the agent reasoning in real-time.

**(2:30 - 3:30) The Wow Moment: Whistleblower vs. IT Logging**
- Focus on the `CRITICAL` severity conflict.
- Explain the narrative: HR promises anonymity to whistleblowers. IT demands total visibility of all traffic.
- Expand the card: Show the exact passage highlights. Point out the `[Foundry IQ · critical confidence]` tags proving this isn't hallucinated.
- This is the "Aha!" moment.

**(3:30 - 4:30) Impact & Remediation**
- Walk through the downstream agents' work: Show the **Risk Score** and the **Enterprise Risk Banner**.
- Click the **Approve** button on the conflict to trigger the `RemediationWorkflow`. Explain how ConflictSense moves beyond detection into actionable business value.

**(4:30 - 5:00) Conclusion & Q&A**
- Reiterate the core pillars: **Grounded** (Azure AI Search), **Reasoning-focused** (Multi-agent), and **Accessible** (WCAG compliant).
- Open the floor for questions.
