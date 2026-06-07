# ConflictSense Data Contracts

## Research Inputs Used
- research/Pasted text(47).txt
- research/ConflictSense_UI.jsx

## Frozen Decisions Applied
- Conflict output must include reasoning, citations, and metadata.

## Assumptions
- None.

---

## 1. PolicyStatement
Represents a single statement extracted from a document by the DocumentAnalyzer.
```typescript
interface PolicyStatement {
    document: string;         // e.g., "IT_Security_Policy.md"
    section: string;          // e.g., "§4.2"
    passage: string;          // Exact text from the document
    confidence: number;       // Foundry IQ retrieval confidence (0.0 - 1.0)
    topic: string;            // The query topic
}
```

## 2. ConflictRecord
Represents a detected contradiction.
```typescript
interface ConflictRecord {
    id: string;               // Unique identifier
    has_conflict: boolean;
    title: string;
    severity: "CRITICAL" | "HIGH" | "MEDIUM";
    confidence: number;       // 0-100%
    sources: string[];        // Array of source references, e.g., "IT_Security_Policy.md §4.2"
    affected: string;         // Affected population/systems (prose)
    deadline: string | null;  // e.g., "July 1, 2026 — 24 days"
    resolution: string;       // Recommended resolution (prose)
    isSurprise?: boolean;     // True if conflict is an unexpected finding
    citations: PolicyStatement[]; // Underlying evidence
}
```

## 3. TraceStep
Represents a step in the Reasoning Trace UI.
```typescript
interface TraceStep {
    agent: string;            // Agent name (e.g., "ConflictDetector")
    agentColor: string;       // Hex color code for UI
    time: string;             // Execution time, e.g., "0.8s"
    query?: string | null;    // Query text, if applicable
    citations?: PolicyStatement[] | null; 
    conclusion: string | null; // Prose reasoning text
    severity?: string | null;
    confidence?: number | null;
    isSurprise?: boolean;
}
```
