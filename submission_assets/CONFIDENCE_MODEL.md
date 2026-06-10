# Confidence Threshold Model

ConflictSense utilizes a strict confidence scoring model to determine how policy conflicts are classified, routed, and displayed. This model is critical for minimizing alert fatigue and ensuring that high-risk liabilities are prioritized.

## The Model

The system assigns a percentage-based confidence score to every detected conflict, derived from the semantic clarity of the overlap and the exactness of the Azure AI Search retrieval.

### 90–100%: Critical
* **Definition:** Unambiguous, explicit contradiction between two or more active policies.
* **UI Presentation:** Rendered with a red `#F09595` severity header and an "UNEXPECTED" flag if discovered without a direct prompt.
* **Action:** Immediately elevated to the primary dashboard. Requires mandatory human approval or escalation.

### 75–89%: High Confidence
* **Definition:** Strong likelihood of conflict based on the semantic similarity of obligations, though exact keywords may differ.
* **UI Presentation:** Rendered with a warning `#FAC775` severity header.
* **Action:** Surfaced on the primary dashboard for human review.

### 60–74%: Needs Human Review
* **Definition:** A potential edge-case or context-dependent conflict. The AI detects tension but cannot definitively rule out compatibility without human context.
* **UI Presentation:** Rendered with standard information styling.
* **Action:** Included in the summary but may require the user to drill down to see the full reasoning trace.

### Below 60%: Informational
* **Definition:** Low-confidence connections, often resulting from broad, generalized policy statements.
* **UI Presentation:** Kept off the main dashboard entirely.
* **Action:** Logged silently in the reasoning trace for complete auditability, but hidden from the user to prevent noise.

## Architectural Note

The backend `ConflictDetector` agent is responsible for generating this score, but it relies completely on the quality of the passages provided by the `AzureSearchRetriever`. Without the semantic ranking provided by Azure AI Search, confidence scores would drop precipitously across the board.
