# ConflictSense Architecture Diagram Mermaid

```mermaid
flowchart TD
    U[User] --> UI[SSE UI]
    UI --> API[FastAPI Backend]
    API --> ORCH[Orchestrator]
    ORCH --> DA[DocumentAnalyzer]
    DA --> FIQ[Azure Foundry IQ]
    DA --> CD[ConflictDetector]
    CD --> CV[ConflictValidator]
    CV --> IA[ImpactAssessor]
    IA --> HG[Approval Gate]

    HG --> UI

    ORCH -. Tier 2: backup model .-> FIQ
    ORCH -. Tier 3: mock mode .-> MOCK[Precomputed Mock Responses]
    MOCK --> UI

    HUMAN[Human Reviewer] --- HG
    CIT[Grounded citations] --- FIQ
```

## Notes
- The fallback path is intentionally shown as dashed edges so it reads as resilience, not as a second architecture.
- The human boundary is explicit because enterprise judges care about control, not only capability.
