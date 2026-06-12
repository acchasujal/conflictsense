import json
import os

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
            "status": "loading",
            "source_dir": "knowledge_base"
        }
    })

# 2. Collect conflicts
conflicts = []
for fname in scenarios:
    path = os.path.join("data", "precomputed", fname)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for event in data:
                if event.get("event") in ["conflict_detected", "conflict_emitted", "trace_step", "risk_validated", "risk_category_identified"]:
                    # We will only pull the trace steps and conflicts
                    conflicts.append(event)

out_events.extend(conflicts)

# 3. Add complete event
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
