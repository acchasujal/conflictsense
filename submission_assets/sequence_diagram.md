# ConflictSense Sequence Diagram

## Demo Sequence
```mermaid
sequenceDiagram
    autonumber
    actor Judge as Judge/User
    participant UI as SSE UI
    participant API as FastAPI Backend
    participant OA as Orchestrator
    participant DA as DocumentAnalyzer
    participant CD as ConflictDetector
    participant CA as ConflictValidator
    participant IA as ImpactAssessor
    participant FIQ as Azure Foundry IQ
    participant HG as Approval Gate

    Judge->>UI: Click "Run Analysis"
    UI->>API: POST /analyze
    API->>OA: Start analysis pipeline

    OA->>DA: Analyze each policy document
    DA->>FIQ: Query source document with grounded citations
    FIQ-->>DA: Section-level evidence and citations
    DA-->>OA: Structured findings

    OA->>CD: Compare findings across documents
    CD-->>OA: Candidate contradictions

    OA->>CA: Validate confidence and citation count
    CA-->>OA: Approved or rejected finding

    OA->>IA: Assess affected people, teams, and systems
    IA->>FIQ: Retrieve grounded impact context
    FIQ-->>IA: Scope and entity evidence
    IA-->>OA: Impact summary

    OA-->>API: Stream reasoning trace via SSE
    API-->>UI: Live paragraphs, citations, and status updates
    UI-->>Judge: Show contradiction and supporting evidence

    Judge->>HG: Approve, reject, or escalate
    HG-->>API: Human decision recorded
    API-->>UI: Final state updated
```

## What This Sequence Proves
- The system does not jump straight to an answer.
- It retrieves evidence first, then reasons over it.
- It validates findings before showing them.
- It keeps a human in the loop for the last mile.

## Judge-Friendly Read
The sequence is intentionally easy to explain in under 20 seconds:
1. Load policies.
2. Ground each document with Foundry IQ.
3. Detect the contradiction.
4. Validate it.
5. Stream the reasoning trace.
6. Ask a human what to do next.
