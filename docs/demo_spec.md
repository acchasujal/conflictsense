# ConflictSense Demo Specification

## Research Inputs Used
- research/00_frozen_decisions.md
- research/Pasted text(47).txt

## Frozen Decisions Applied
- 90-second duration.
- Focused on Anonymity Conflict.

## Assumptions
- Standard hackathon demo constraints (screen share, rapid pacing).

---

## 1. Demo Parameters
- **Duration:** 90 seconds.
- **Narrative Hook:** "Nexora's employees believe they can report harassment anonymously. They cannot. The IT Security Policy logs every system action, no exceptions. ConflictSense found this without being asked to look there."

## 2. Shot-by-Shot Sequence

### 0:00 - 0:15 | The Problem
- **Visual:** Dashboard idle state, showing the 7 loaded policy documents.
- **V/O:** "In enterprise environments, policies are written in silos. HR doesn't talk to IT. Legal doesn't talk to Finance. This creates structural impossibilities. Today we're analyzing Nexora Technologies."

### 0:15 - 0:35 | The Analysis Run
- **Visual:** Click "Run Analysis". The Reasoning Trace panel lights up. Agents start generating prose conclusions.
- **V/O:** "We trigger ConflictSense. Notice the Reasoning Trace. It's not just returning JSON—it's using Azure Foundry IQ to retrieve section-level citations from each document and reason through them in plain English."

### 0:35 - 0:55 | The Reveal (Anonymity Conflict)
- **Visual:** The "Anonymity guarantee is technically impossible" conflict appears. Cursor highlights the reasoning paragraph.
- **V/O:** "Here's the critical finding. The Whistleblower Policy guarantees anonymity. But the IT Security Policy mandates identity logging for every system action. It is technically impossible to report harassment anonymously at this company."

### 0:55 - 1:15 | Grounding & Reliability
- **Visual:** Hover over the Foundry IQ citations.
- **V/O:** "Because this is powered by Foundry IQ, every claim is grounded. There are no LLM hallucinations here. This output is fully auditable."

### 1:15 - 1:30 | Human-in-the-Loop & Conclusion
- **Visual:** Click "Escalate to legal" on the Human Approval Gate.
- **V/O:** "ConflictSense flags the issue, but takes no autonomous action. It requires human approval. We escalate to legal. This is Responsible AI solving real enterprise risk. Thank you."

## 3. Fallback Assurance
If the Azure API fails during the live demo, the orchestrator instantly falls back to Tier 3 Mock Mode. The demo will complete flawlessly, displaying a `[MOCK MODE]` tag to maintain honesty without failing the presentation.
