# ConflictSense Test Corpus

## Research Inputs Used
- research/ConflictSense_UI.jsx

## Frozen Decisions Applied
- 3 benchmark conflicts.

## Assumptions
- Synthetic data logic directly applies.

---

## 1. Positive Evaluation Cases (Must Detect)

**Case 1: Anonymity Conflict**
- *Sources:* Whistleblower_Policy.md vs IT_Security_Policy.md
- *Expected:* CRITICAL severity. Detect that anonymity is promised but technically impossible due to mandatory IT logging.

**Case 2: Data Residency Trilemma**
- *Sources:* IT_Security_Policy.md vs HR_Remote_Work_Policy.md vs DPDP_Compliance_Directive.md
- *Expected:* CRITICAL severity. Detect that 34 India-resident remote workers cannot simultaneously satisfy US-server mandates, global remote work allowances, and Indian data residency requirements.

**Case 3: Incident Reporting Gap**
- *Sources:* IT_Security_Policy.md vs Whistleblower_Policy.md
- *Expected:* CRITICAL severity. Detect parallel notification obligations that clash with FCA 72-hour breach timelines.

## 2. Negative Evaluation Cases (Must NOT Detect)

**Case 4: Ambiguous Wording**
- *Description:* Two policies use different synonyms for "vacation days".
- *Expected Output:* NO CONFLICT. Language ambiguity without operational impossibility is ignored.

**Case 5: Lack of Citations**
- *Description:* A prompted hallucination where the LLM claims a conflict but cannot provide 2 distinct Foundry IQ citations.
- *Expected Output:* BLOCKED. Fails citation validation step.

## 3. Edge Cases

**Case 6: Low Confidence**
- *Description:* A conflict is detected with 55% confidence.
- *Expected Output:* Routed to `UNCERTAIN` human review queue. NOT shown on main dashboard.
