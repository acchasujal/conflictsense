# ConflictSense Judging Alignment Matrix

## Research Inputs Used
- research/Pasted text(47).txt
- research/00_frozen_decisions.md

## Frozen Decisions Applied
- 20% weight on Reasoning & Multi-step thinking.

## Assumptions
- None.

---

## 1. The Alignment Matrix

| Feature | Judging Criterion | Evidence Produced | Demo Moment |
| :--- | :--- | :--- | :--- |
| **Foundry IQ Per-Document Querying** | Technical Complexity / RAG Best Practices | Section-level citations instead of generic document summaries. | 0:25 - Hovering over exact policy citations. |
| **Reasoning Trace UI** | Reasoning & Multi-step Thinking (20%) | Prose paragraphs showing logical deduction, not just API logs. | 0:40 - Reading the Anonymity impossibility prose out loud. |
| **Human Approval Gate** | Responsible AI | UI blocking autonomous execution until manual approval. | 1:15 - Clicking "Escalate to legal" instead of auto-resolving. |
| **3-Tier Fallback Chain** | Reliability / Robustness | Guaranteed demo completion via mock mode. | N/A (or visible `[MOCK MODE]` if API actually fails). |
| **Synthetic Enterprise Domain** | Value & Impact | Detecting a regulatory contradiction with real fines (DPDP). | 0:50 - Mentioning the July 1, 2026 deadline. |

## 2. Feature Creep Prevention
Any proposed feature that does not map directly to a row in this matrix MUST be rejected. For example:
- *Adding a Chatbot UI:* REJECTED. Takes focus away from the Reasoning Trace.
- *Integrating Fabric IQ:* REJECTED. Dilutes the Foundry IQ narrative and introduces reliability risk.
- *Expanding to 20 agents:* REJECTED. Decreases reliability without increasing judging score.
