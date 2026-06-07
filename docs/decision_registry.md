# ConflictSense Decision Registry

## Research Inputs Used
- research/00_frozen_decisions.md
- research/Pasted text(47).txt
- research/ConflictSense_UI.jsx

## Frozen Decisions Applied
- The Decision Registry itself is a governance layer and source of truth.

## Assumptions
- No new assumptions; extracting strictly from research.

---

### [FROZEN] Project Selection
- **Decision:** ConflictSense is the selected project.
- **Reason:** Maximizes probability of winning an Agents League award.
- **Supporting Evidence:** Hackathon focus on reasoning and multi-step thinking.
- **Source Files:** research/00_frozen_decisions.md
- **Confidence:** High

### [FROZEN] Reasoning Trace as Primary Product Surface
- **Decision:** The Reasoning Trace must show prose reasoning, not timestamped function calls, and is the primary UI focus.
- **Reason:** Judges evaluate "Reasoning & Multi-step Thinking" criterion (20% of total score).
- **Supporting Evidence:** "The trace must show prose reasoning — intermediate conclusions written as sentences... The one thing that will determine whether you win: The reasoning trace."
- **Source Files:** research/Pasted text(47).txt
- **Confidence:** High

### [FROZEN] Reliability Over Agent Count
- **Decision:** A 3-tier fallback chain (Primary GPT-4o, Backup GPT-4o-mini, Pre-computed mock) is mandatory.
- **Reason:** A broken demo scores 0. The demo must complete under any circumstance.
- **Supporting Evidence:** "Reliability > agent count", "Tier 3 — Pre-computed mock (demo always completes)"
- **Source Files:** research/00_frozen_decisions.md, research/Pasted text(47).txt
- **Confidence:** High

### [FROZEN] Foundry IQ Integration
- **Decision:** Foundry IQ is mandatory for grounded, per-document retrieval.
- **Reason:** Enables section-level citations, prevents hallucinations, avoids context overflow. Without it, the product is not auditable.
- **Supporting Evidence:** "Foundry IQ is mandatory", "Without Foundry IQ, you concatenate all documents into one prompt and lose per-source attribution."
- **Source Files:** research/00_frozen_decisions.md, research/Pasted text(47).txt
- **Confidence:** High

### [FROZEN] Human Approval Gate
- **Decision:** No conflict enters the resolution workflow or autonomous action without explicit human approval.
- **Reason:** Ensures Responsible AI practices and prevents unintended policy/system modifications.
- **Supporting Evidence:** "Human Approval Gate mandatory", UI components showing "Escalate", "Approve", "Mark false positive".
- **Source Files:** research/00_frozen_decisions.md, research/ConflictSense_UI.jsx
- **Confidence:** High

### [FROZEN] Fabric IQ Excluded
- **Decision:** Fabric IQ will not be used in this project.
- **Reason:** Focusing on Foundry IQ integration scope.
- **Supporting Evidence:** "Fabric IQ excluded"
- **Source Files:** research/00_frozen_decisions.md
- **Confidence:** High

### [FROZEN] 90-Second Demo Target
- **Decision:** The demo must be centered around the anonymity conflict and last 90 seconds.
- **Reason:** Optimizing for judging format.
- **Supporting Evidence:** "90 second demo", "Demo centered around anonymity conflict"
- **Source Files:** research/00_frozen_decisions.md, research/Pasted text(47).txt
- **Confidence:** High

### [FROZEN] Technology Stack
- **Decision:** React + Vite (Frontend) and FastAPI (Backend).
- **Reason:** Known reliable stack for rapid prototyping.
- **Supporting Evidence:** "React + FastAPI stack", file structure mentioning `frontend/ src/ App.jsx` and `backend/ main.py`
- **Source Files:** research/00_frozen_decisions.md, research/Pasted text(47).txt
- **Confidence:** High

### [FROZEN] Synthetic Enterprise Target
- **Decision:** Nexora Technologies is the synthetic enterprise, featuring 7 specific policy documents.
- **Reason:** Creates a realistic, constrained environment with built-in impossible conflicts.
- **Supporting Evidence:** "Synthetic enterprise = Nexora Technologies", 7 distinct policy documents listed in knowledge_base.
- **Source Files:** research/00_frozen_decisions.md, research/Pasted text(47).txt, research/ConflictSense_UI.jsx
- **Confidence:** High

### [TENTATIVE] Work IQ Integration
- **Decision:** Potential integration of Work IQ signals as a side input.
- **Reason:** Mentioned in architecture diagram notes.
- **Supporting Evidence:** "Work IQ signals as a side input"
- **Source Files:** research/Pasted text(47).txt
- **Confidence:** Medium

### [OPEN] Final Risk Scoring Methodology
- **Decision:** Exact scoring formulas for RiskQuantifier are not fully standardized beyond HIGH/MEDIUM/LOW mappings.
- **Reason:** Research indicates severity mapping, but exact sub-scores might need tuning.
- **Supporting Evidence:** Missing exact numerical weights in the research.
- **Source Files:** N/A
- **Confidence:** Low
