# ConflictSense Product Requirements Document (PRD)

## Research Inputs Used
- research/00_frozen_decisions.md
- research/Pasted text(47).txt
- research/ConflictSense_UI.jsx

## Frozen Decisions Applied
- Human Approval Gate mandatory.
- Reliability > agent count.
- Foundry IQ mandatory for grounded citations.
- 90-second demo centered on anonymity conflict.

## Assumptions
- None.

---

## 1. Product Overview
ConflictSense detects policy contradictions within enterprise documents by leveraging a multi-agent system powered by Azure Foundry IQ.

## 2. Core Features

### 2.1 Multi-Agent Pipeline
- **DocumentAnalyzer:** Retrieves per-document grounded citations from Foundry IQ.
- **ConflictDetector:** Compares statements and identifies logical impossibilities.
- **ImpactAssessor:** Quantifies affected populations via Foundry IQ entity extraction.
- **RiskQuantifier:** Maps conflicts to regulatory penalties (e.g., DPDP Act §91).
- **ResolutionRecommender:** Suggests actionable resolutions based on regulatory context.

### 2.2 Reasoning Trace UI
- **Prose Output:** Must output natural language paragraphs for reasoning, not just JSON or timestamped labels.
- **Transparency:** The UI must display intermediate reasoning for each agent step.

### 2.3 Human Approval Gate
- **Requirement:** Any conflict entering the resolution workflow requires human approval.
- **Actions:** The UI must provide options to "Approve finding", "Mark false positive", or "Escalate to legal".
- **Rule:** No autonomous action is permitted without explicit click-based approval.

### 2.4 Reliability & Fallback
- **Requirement:** The system must never crash during a demo.
- **Implementation:** 3-tier fallback strategy (Primary -> Backup -> Mock).
- **Confidence Thresholds:**
  - High (0.85-1.0): Show in dashboard.
  - Medium (0.65-0.85): Review Required badge.
  - Low (<0.65): Human review queue only.
- **Citation Rule:** Any conflict finding with fewer than 2 citations is discarded.

## 3. Demo Requirements
- **Duration:** 90 seconds.
- **Focus:** The structural impossibility of anonymity guarantees (Whistleblower Policy vs. IT Security Policy).
- **Completion Guarantee:** Demo must complete even if Azure API keys are invalid.
