# ConflictSense Research Synthesis

## Research Inputs Used
- research/00_frozen_decisions.md
- research/Pasted text(47).txt
- research/ConflictSense_UI.jsx

## Frozen Decisions Applied
- Extracted purely actionable findings, no fluff, no alternative architectures.

## Assumptions
- No assumptions; extracted directly from research text.

---

### Winner Patterns
- **Prose Reasoning:** The reasoning trace must show intermediate conclusions written as full sentences, not timestamped function calls. This addresses the 20% "Reasoning & Multi-step Thinking" criterion.
- **Grounded Assertions:** The affected employee count and citations must come from entity extraction via Foundry IQ, not hardcoded inferences (hallucinations).

### Loser Patterns
- **Concatenation Overload:** Passing all documents into a single prompt leads to context overflow, hallucinated paraphrasing, and loss of section-level citations.
- **Brittle Demos:** Demos that crash or show unhandled exceptions score zero.

### Judge Psychology
- **Auditability Focus:** Outputs must be shown to regulators. Everything must be grounded and auditable.
- **Responsible AI Constraints:** Judges value systems that block low-confidence findings and enforce human-in-the-loop approval before autonomous action.

### Microsoft Incentives
- **Azure Foundry IQ Showcase:** Demonstrating that Foundry IQ enables multi-source, grounded comparison that is impossible otherwise. Emphasize "auditable".

### Demo Lessons
- **Anonymity Hook:** Center the demo on the anonymity conflict: "Nexora's employees believe they can report harassment anonymously. They cannot... IT logs every action."
- **Mock Mode:** A visible `[MOCK MODE]` fallback guarantees demo completion if Azure API fails.

### Reliability Lessons
- **3-Tier Fallback Chain:**
  - Tier 1: Primary Model (gpt-4o, 10s timeout)
  - Tier 2: Backup Model (gpt-4o-mini, 15s timeout)
  - Tier 3: Pre-computed Mock (never fails)
- **Confidence Thresholds:**
  - High (0.85-1.0): Auto-classify, show in dashboard.
  - Medium (0.65-0.85): Show with REVIEW REQUIRED badge.
  - Low (<0.65): Route to human review queue only.
- **Citation Validation:** Any conflict with <2 Foundry IQ citations must be blocked.

### Competitive Landscape
- The focus on "Reasoning Trace" is the primary differentiator against standard RAG/chatbots.

### Foundry IQ Insights
- **Per-Document Querying:** Querying topics per individual document yields section-level citations and prevents context overflow.
- **Requirement:** `require_grounded_citations=True` must be used.

### Enterprise Value Insights
- **Structural Impossibility:** Finding contradictions baked into architecture/policies, which humans miss because documents are siloed (e.g., HR vs. IT vs. Legal).
- **Compliance Deadlines:** Highlighting deadlines (e.g., DPDP Act) drives urgency.

### ConflictSense Selection Rationale
- High visual impact (Reasoning Trace UI).
- Real-world enterprise value (Compliance and Policy contradictions).
- Hard dependency on Microsoft tech (Foundry IQ for multi-document grounding).
