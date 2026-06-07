# ConflictSense System Architecture

## Research Inputs Used
- research/00_frozen_decisions.md
- research/Pasted text(47).txt

## Frozen Decisions Applied
- React + FastAPI stack
- 3-tier fallback chain
- Foundry IQ integration

## Assumptions
- None.

---

## 1. High-Level Architecture
ConflictSense is composed of three primary layers:
1. **Frontend:** React + Vite application for rendering the Reasoning Trace UI and Human Approval Gate.
2. **Backend:** FastAPI application exposing `/analyze`, `/approve`, and `/reject` endpoints.
3. **Agent Orchestrator:** A Python class (`ConflictSenseOrchestrator`) coordinating the 5-agent pipeline and fallback logic.

## 2. Component Diagram

```
[Synthetic Knowledge Base (7 Policy Docs)]
        │
        ▼
   [Foundry IQ] <──────┐
        │              │
        ▼              │
[Agent Orchestrator] ──┘ (Queries & Citations)
        │
        ├── 1. DocumentAnalyzer
        ├── 2. ConflictDetector
        ├── 3. ImpactAssessor
        ├── 4. RiskQuantifier
        └── 5. ResolutionRecommender
        │
        ▼
[Confidence Filter & Citation Validation]
        │
        ▼
    [FastAPI Backend]
        │
        ▼
[React Frontend] (Reasoning Trace UI)
        │
        ▼
[Human Approval Gate]
```

## 3. The Orchestrator (`ConflictSenseOrchestrator`)
Responsible for managing the execution flow and enforcing reliability:
- **Tier 1:** `gpt-4o` via Azure Foundry IQ (10s timeout).
- **Tier 2:** `gpt-4o-mini` via Azure Foundry IQ (15s timeout).
- **Tier 3:** Pre-computed mock responses (guarantees completion).

## 4. Foundry IQ Integration
- Acts as a central hub, accessed by agents for grounded retrieval.
- Prevents context overflow by answering per-document queries rather than using document concatenation.
