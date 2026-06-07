# ConflictSense Foundry IQ Specification

## Research Inputs Used
- research/Pasted text(47).txt

## Frozen Decisions Applied
- Foundry IQ mandatory for grounded citations.
- Per-document querying strategy.

## Assumptions
- None.

---

## 1. Core Integration Strategy
ConflictSense uses Azure Foundry IQ as the absolute source of truth for all policy and regulatory knowledge. It avoids standard RAG concatenation.

## 2. Query Patterns

### 2.1 Per-Document Queries (DocumentAnalyzer)
**Purpose:** Prevent context window overflow and preserve section-level attribution.
**Pattern:**
```python
response = foundry_iq.query(
    query=f"What rule or policy applies to: {topic}?",
    knowledge_source_ids=[doc.id],
    require_grounded_citations=True,
)
```

### 2.2 Entity/Scope Queries (ImpactAssessor)
**Purpose:** Ensure affected populations are grounded, not hallucinated.
**Pattern:**
```python
response = foundry_iq.query(
    query=f"Which employee groups, systems, or teams are mentioned in connection with {conflict_topic}?",
    knowledge_source_ids=[all_relevant_doc_ids],
    require_grounded_citations=True,
)
```

### 2.3 Regulatory Queries (RiskQuantifier & ResolutionRecommender)
**Purpose:** Anchor risks and resolutions in actual legal text.
**Pattern:**
```python
response = foundry_iq.query(
    query=f"What are the penalties for {regulation_name} non-compliance?",
    knowledge_source_ids=[regulatory_doc_ids],
    require_grounded_citations=True,
)
```

## 3. The "Auditable" Requirement
Because every query mandates `require_grounded_citations=True`, every assertion produced by ConflictSense is traceable to a specific source document, section, and exact passage. This fulfills the "Auditable" requirement for judges and regulators.
