# ConflictSense Acceptance Criteria

## Research Inputs Used
- research/00_frozen_decisions.md
- research/Pasted text(47).txt

## Frozen Decisions Applied
- Reliability, Foundry IQ integration, UI trace requirements.

## Assumptions
- None.

---

## 1. Pipeline Execution
- **[ ]** Pipeline must complete end-to-end analysis on 7 documents within 10 seconds.
- **[ ]** DocumentAnalyzer MUST query Foundry IQ with `require_grounded_citations=True`.
- **[ ]** ConflictDetector MUST output prose reasoning paragraphs, not JSON dumps or timestamped action labels.

## 2. Reliability & Safety
- **[ ]** System MUST successfully fall back to Tier 3 Mock Mode and complete the demo if an invalid Azure API key is provided.
- **[ ]** ConflictDetector MUST discard any finding that contains fewer than 2 distinct Foundry IQ citations.
- **[ ]** Findings with confidence < 0.65 MUST be routed away from the main dashboard.

## 3. User Interface
- **[ ]** UI MUST render the Reasoning Trace as a visible, scrolling feed.
- **[ ]** UI MUST implement the Human Approval Gate (Approve, Mark False Positive, Escalate).
- **[ ]** UI MUST display `[MOCK MODE]` if Tier 3 fallback is activated.

## 4. Documentation & Demo
- **[ ]** `docs/ablation_test.md` MUST exist and log the exact degraded performance of removing Foundry IQ.
- **[ ]** The 90-second demo MUST successfully showcase the anonymity conflict (Whistleblower vs. IT Security).
