# Final Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor Judge as Judge
    participant UI as SSE UI
    participant API as FastAPI Backend
    participant ORCH as Orchestrator
    participant DA as DocumentAnalyzer
    participant FIQ as Azure Foundry IQ
    participant CD as ConflictDetector
    participant CV as ConflictValidator
    participant IA as ImpactAssessor
    participant HG as Approval Gate

    Judge->>UI: Run analysis
    UI->>API: POST /analyze
    API->>ORCH: Start pipeline

    ORCH->>DA: Analyze source documents
    DA->>FIQ: Query each document with grounded citations
    FIQ-->>DA: Retrieved policy evidence
    DA-->>ORCH: Structured document findings

    ORCH->>CD: Compare evidence across documents
    CD-->>ORCH: Conflict candidates

    ORCH->>CV: Validate citations and confidence
    CV-->>ORCH: Accept or reject finding

    ORCH->>IA: Assess impacted people, teams, systems
    IA->>FIQ: Ground scope and entity references
    FIQ-->>IA: Impact evidence
    IA-->>ORCH: Impact summary

    ORCH-->>API: Stream reasoning trace via SSE
    API-->>UI: Live explanation, citations, status
    UI-->>Judge: Show the validated conflict

    Judge->>HG: Approve, reject, or escalate
    HG-->>API: Human decision recorded
    API-->>UI: Final state updated
```

## Why This Version Is Better
- Shorter and cleaner for PDF export.
- Focuses on the approved pipeline only.
- Clearly separates evidence retrieval, validation, and human review.
- Reads well when narrated to executives.
