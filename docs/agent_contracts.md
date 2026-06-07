# ConflictSense Agent Contracts

## Research Inputs Used
- research/Pasted text(47).txt

## Frozen Decisions Applied
- Exact system prompts and reasoning trace behavior defined.
- Confidence thresholds and mock response routing.

## Assumptions
- None.

---

## 1. DocumentAnalyzer
**Role:** Policy document analyst.
**Action:** Receives grounded citations from a single enterprise policy document. Extracts specific rules or constraints applying to a topic.
**Prompt Requirements:**
- "Return ONLY the exact claim made by this document — do not infer, extrapolate, or summarize. If the document is silent on the topic, say so explicitly."
**Output Format:** `{statement: string, scope: string, effective_date: string, is_silent: boolean}`

## 2. ConflictDetector
**Role:** Policy conflict analyst.
**Action:** Compares statements from DocumentAnalyzer. Identifies pairs/groups making incompatible claims.
**Prompt Requirements:**
- "Identify any pair or group of statements that make incompatible claims — claims that cannot simultaneously be satisfied for the same employee population."
- "Explain, in plain language, WHY the conflict is logically impossible — not just that the statements differ."
**Output Format:** `{has_conflict: boolean, conflict_pairs: [...], reasoning: string, severity: "CRITICAL"|"HIGH"|"MEDIUM", confidence: float}`
**Constraint:** If confidence < 0.65, status = UNCERTAIN.

## 3. ImpactAssessor
**Role:** Scope quantifier.
**Action:** Queries Foundry IQ for employee groups, systems, or teams mentioned in connection with a conflict topic. Grounded in actual policy text, not LLM inference.
**Output Requirement:** Generates prose detailing the affected population and systems.

## 4. RiskQuantifier
**Role:** Grounded enterprise risk analyst.
**Action:** Receives only validated conflicts after ImpactAssessor. Converts the validated conflict, grounded citations, and impact assessment into a RiskAssessment.
**Output Requirement:** Generates `risk_level`, `risk_score`, `risk_categories`, `reasoning`, `supporting_evidence`, `confidence`, `affected_entities`, and `potential_consequences`.
**Constraint:** Must not process rejected conflicts. Must not invent employee counts, penalties, financial exposure, or percentages. If evidence is unavailable, uncertainty must be stated explicitly.

## 5. ResolutionRecommender
**Role:** Fix proposer.
**Action:** Queries Foundry IQ for resolution approaches based on regulatory best practices.
**Output Requirement:** Generates actionable resolution steps, with owner assignments and deadlines.
