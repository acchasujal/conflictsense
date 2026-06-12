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
        "agent": "Document Analysis",
        "agentColor": "#85B7EB",
        "time": "0.4s",
        "conclusion": "Knowledge Base Loaded: Successfully indexed 7 enterprise policies into vector store.",
        "confidence": 100,
        "citations": []
    },
    {
        "agent": "Azure Search Grounding",
        "agentColor": "#85B7EB",
        "time": "1.2s",
        "conclusion": "Cross-Policy Review Started: Initiating parallel comparison across all policy boundaries.",
        "confidence": 98,
        "citations": []
    },
    {
        "agent": "Conflict Detection",
        "agentColor": "#F09595",
        "time": "2.1s",
        "conclusion": "Governance Contradictions Identified: Detected 5 structurally impossible compliance mandates across HR, IT, Legal, and Finance.",
        "confidence": 95,
        "citations": []
    },
    {
        "agent": "Conflict Validation",
        "agentColor": "#D085EB",
        "time": "1.8s",
        "conclusion": "Logic Validation: Verified that the 5 identified contradictions are structural impossibilities, not just missing guidance.",
        "confidence": 96,
        "citations": []
    },
    {
        "agent": "Impact Assessment",
        "agentColor": "#EBD085",
        "time": "1.4s",
        "conclusion": "Human Impact Assessment Complete: Mapped contradictions to affected employee groups, identifying significant inclusion and safety risks.",
        "confidence": 92,
        "citations": []
    },
    {
        "agent": "Risk Quantification",
        "agentColor": "#F0B05A",
        "time": "0.9s",
        "conclusion": "Risk Prioritization Complete: Categorized findings by severity (Critical, High, Medium) based on legal exposure and blast radius.",
        "confidence": 96,
        "citations": []
    },
    {
        "agent": "Resolution Generation",
        "agentColor": "#5AB0F0",
        "time": "1.1s",
        "conclusion": "Executive Summary Generated: Compiled enterprise audit report and remediation roadmap for leadership review.",
        "confidence": 99,
        "citations": []
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
        "execution_time_s": 8.9
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
