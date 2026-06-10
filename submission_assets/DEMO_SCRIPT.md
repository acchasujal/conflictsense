# ConflictSense Demo Script

**Target Length:** 2 Minutes max.
**Pacing:** Fast, energetic, business-focused.

---

### [0:00 - 0:15] The Hook & Problem
*(Show slide or blank screen with just the ConflictSense logo)*
**Speaker:** "Last year, a Fortune 500 company was fined $5 Million because their IT Data Retention policy contradicted their EU Privacy policy. Human auditors missed it. Today, I'm going to show you how ConflictSense uses Azure AI Search and a multi-agent swarm to ensure that never happens again."

### [0:15 - 0:30] The Setup
*(Show the ConflictDashboard in Idle state)*
**Speaker:** "Here is our enterprise knowledge base. We have 7 massive policy documents spanning HR, IT, and Finance. We've just drafted a new Data Privacy Directive. Let's see if it breaks anything."
*(Click 'Run Analysis')*

### [0:30 - 1:00] The Magic (Agent Pipeline)
*(Focus on the Agent Pipeline and Reasoning Trace as they light up)*
**Speaker:** "This is not a simple RAG wrapper. You are watching our deterministic multi-agent pipeline in real-time. 
First, our `DocumentAnalyzer` uses **Azure AI Search's Semantic Ranker** to pull only the most relevant, highly-correlated chunks across all departments.
Then, the `ConflictDetector` identifies contradictions, and crucially, hands them to a `ConflictValidator`—an adversarial agent designed to eliminate false positives and hallucinations."

### [1:00 - 1:30] The Reveal & Business Impact
*(Focus shifts to the red 'Critical Conflict Detected' card and Executive Dashboard)*
**Speaker:** "And there it is. A critical conflict. IT mandates US servers, but the new HR policy allows global remote work for data handlers. 
Our `RiskQuantifier` agent has immediately translated this technical conflict into executive business terms: an estimated $4.2M compliance exposure."

### [1:30 - 1:50] The Resolution (Human Approval Gate)
*(Click on the conflict to expand the Microsoft Teams Approval Gate)*
**Speaker:** "But AI should not rewrite enterprise policy autonomously. Our `ResolutionRecommender` generates a remediation plan and sends it directly to a Microsoft Teams Approval Gate. The Chief Compliance Officer reviews the immutable reasoning trace and clicks 'Approve'."

### [1:50 - 2:00] The Close
*(Zoom out to show the full dashboard)*
**Speaker:** "Millions in fines avoided. Weeks of manual auditing reduced to seconds. This is ConflictSense—Enterprise Governance, powered by Azure."
