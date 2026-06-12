import json
import os
import uuid

scenarios = [
    "scenario_1_data_residency.json",
    "scenario_2_anonymous_reporting.json",
    "scenario_3_cross_border.json",
    "scenario_4_vendor_compliance.json",
    "scenario_5_disability_accommodation.json"
]

out_events = []
# 1. Add some initial document_loaded events
docs = [
    "Employee_Handbook.md", "IT_Security_Policy.md", "HR_Remote_Work_Policy.md",
    "Whistleblower_Policy.md", "Data_Governance_Policy.md", "Finance_Expense_Policy.md",
    "DPDP_Compliance_Directive.md"
]
for doc in docs:
    out_events.append({
        "event": "document_loaded",
        "data": {
            "document": doc,
            "status": "loaded",
            "source_dir": "knowledge_base"
        }
    })

# 2. Add custom timeline trace_step events
timeline_steps = [
    {
        "agent": "IngestionAgent",
        "action": "Knowledge Base Loaded",
        "description": "Successfully indexed 7 enterprise policies into vector store.",
        "confidence": 100,
        "evidence_count": 7
    },
    {
        "agent": "CrossPolicyAnalyzer",
        "action": "Cross-Policy Review Started",
        "description": "Initiating parallel comparison across all policy boundaries.",
        "confidence": 98,
        "evidence_count": 0
    },
    {
        "agent": "LogicValidator",
        "action": "Governance Contradictions Identified",
        "description": "Detected 5 structurally impossible compliance mandates.",
        "confidence": 95,
        "evidence_count": 10
    },
    {
        "agent": "RiskAssessor",
        "action": "Human Impact Assessment Complete",
        "description": "Mapped contradictions to affected employee groups and safety risks.",
        "confidence": 92,
        "evidence_count": 5
    },
    {
        "agent": "RiskAssessor",
        "action": "Risk Prioritization Complete",
        "description": "Categorized findings by severity (Critical, High, Medium).",
        "confidence": 96,
        "evidence_count": 5
    },
    {
        "agent": "ExecutiveSummarizer",
        "action": "Executive Summary Generated",
        "description": "Compiled enterprise audit report for leadership review.",
        "confidence": 99,
        "evidence_count": 1
    },
    {
        "agent": "Orchestrator",
        "action": "Analysis Complete",
        "description": "Full KB Analysis finished successfully.",
        "confidence": 100,
        "evidence_count": 0
    }
]

for step in timeline_steps:
    out_events.append({
        "event": "trace_step",
        "data": step
    })


# 3. Collect conflicts (but discard trace_steps from the scenarios to keep our clean timeline)
conflicts = []
for fname in scenarios:
    path = os.path.join("data", "precomputed", fname)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for event in data:
                if event.get("event") in ["conflict_detected", "conflict_emitted", "risk_validated", "risk_category_identified"]:
                    conflicts.append(event)

out_events.extend(conflicts)

# 4. Add complete event
out_events.append({
    "event": "analysis_complete",
    "data": {
        "status": "complete",
        "total_conflicts": 5,
        "uncertain_count": 0,
        "blocked_count": 0,
        "is_mock_mode": True,
        "execution_time_s": 4.1
    }
})

out_events.append({
    "event": "complete",
    "data": {
        "status": "complete",
        "total_conflicts": 5,
        "_meta": {
            "fallback": "DEMO_SCENARIO_REPLAY",
            "execution_mode": "Enterprise Audit Report"
        }
    }
})

out_path = os.path.join("data", "precomputed", "full_kb_analysis.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(out_events, f, indent=2)

print(f"Built full_kb_analysis.json with {len(out_events)} events.")
