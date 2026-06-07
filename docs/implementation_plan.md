# ConflictSense Implementation Plan

## Research Inputs Used
- research/Pasted text(47).txt

## Frozen Decisions Applied
- Day-by-day implementation sequence.

## Assumptions
- None.

---

## Day 1: Foundation
1. Join Agents League Discord.
2. Write all 7 synthetic policy documents in `knowledge_base/` with distinct departmental voices.
3. Upload documents to Foundry IQ and verify base retrieval.
4. Finalize architecture SVG.

## Day 2: DocumentAnalyzer & Reasoning Trace UI
1. Build the Reasoning Trace UI component in React.
2. Define exact prose output text for trace steps.
3. Build `DocumentAnalyzer` against Foundry IQ.
4. Build `ConflictSenseOrchestrator` shell with 3-tier fallback chain.

## Day 3: ConflictDetector
1. Build `ConflictDetector`.
2. Test specifically on Benchmark Conflicts 1, 2, and 3.
3. Implement confidence thresholds and routing logic.
4. Implement citation validation (block if < 2 citations).

## Day 4: Full Pipeline Wiring
1. Build `ImpactAssessor`, `RiskQuantifier`, and `ResolutionRecommender`.
2. Wire all 5 agents into the orchestrator.
3. Run end-to-end reliability test (force invalid API key to trigger mock mode).

## Day 5: Frontend & Demo Flow
1. Build the full 2-panel React dashboard.
2. Implement the Human Approval Gate buttons.
3. Connect React to FastAPI backend.
4. Run full demo end-to-end.

## Day 6: Polish & Documentation
1. Run demo 10 times to catch spinner/loading issues.
2. Conduct the Ablation Test (concatenation vs Foundry IQ) and log results in `docs/ablation_test.md`.
3. Complete `README.md`.

## Day 7: Submission
1. Submit project.
2. Vote in community.
