import json
import os
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "precomputed"

def build_scenario_json(scenario_name, theme, base_conf, mid_conf, final_conf, reqs, risks, recs, citations):
    trace = []
    
    # 1. evidence_retrieved
    trace.append({
        "event": "evidence_retrieved",
        "data": {
            "topic": theme,
            "citation_count": len(citations),
            "documents_queried": 7,
            "silent_documents": ["Handbook.md", "Marketing.md"],
            "is_mock_mode": True
        }
    })
    
    # 2. trace_step (Azure Search)
    trace.append({
        "event": "trace_step",
        "data": {
            "agent": "Azure Search Grounding",
            "agentColor": "#85B7EB",
            "time": "0.4s",
            "query": theme,
            "citations": citations,
            "conclusion": None,
            "severity": None,
            "confidence": None,
            "telemetry": {
                "docs_analyzed": 5,
                "total_citations": len(citations),
                "per_document_meta": []
            }
        }
    })
    
    # 3. conflict_candidate_detected
    trace.append({
        "event": "conflict_candidate_detected",
        "data": {
            "topic": theme,
            "raw_confidence": base_conf,
            "severity": "HIGH",
            "sources": [c["document"] for c in citations]
        }
    })
    
    # 4. conflict_validated
    trace.append({
        "event": "conflict_validated",
        "data": {
            "id": f"{scenario_name}_c1",
            "passed": True,
            "reason": "ok"
        }
    })
    
    # 5. trace_step (Validation)
    trace.append({
        "event": "trace_step",
        "data": {
            "agent": "Conflict Validation",
            "agentColor": "#D085EB",
            "time": "1.2s",
            "query": None,
            "citations": None,
            "conclusion": "Validation passed: structural impossibility confirmed.",
            "severity": None,
            "confidence": None
        }
    })
    
    # 6. risk_assessment_started
    trace.append({
        "event": "risk_assessment_started",
        "data": {
            "id": f"{scenario_name}_c1",
            "topic": theme,
            "conflict": f"{theme} Contradiction"
        }
    })
    
    # 7. trace_step (Impact)
    trace.append({
        "event": "trace_step",
        "data": {
            "agent": "Impact Assessment",
            "agentColor": "#EBD085",
            "time": "0.9s",
            "query": None,
            "citations": None,
            "conclusion": ["Legal", "Compliance", "IT"],
            "severity": None,
            "confidence": None
        }
    })
    
    # 8. risk_category_identified
    for r in risks:
        trace.append({
            "event": "risk_category_identified",
            "data": {
                "id": f"{scenario_name}_c1",
                "category": r,
                "risk_level": "HIGH"
            }
        })
        
    # 9. risk_validated
    trace.append({
        "event": "risk_validated",
        "data": {
            "id": f"{scenario_name}_c1",
            "risk_level": "CRITICAL",
            "risk_score": mid_conf,
            "confidence": mid_conf
        }
    })
    
    # 10. trace_step (Risk Quantification)
    trace.append({
        "event": "trace_step",
        "data": {
            "agent": "Risk Quantification",
            "agentColor": "#F0B05A",
            "time": "1.5s",
            "query": None,
            "citations": ["Multiple regulatory frameworks at risk"],
            "conclusion": f"High probability of non-compliance regarding {theme}",
            "severity": "CRITICAL",
            "confidence": mid_conf
        }
    })
    
    # 11. risk_assessment_complete
    trace.append({
        "event": "risk_assessment_complete",
        "data": {
            "id": f"{scenario_name}_c1",
            "assessment": {
                "risk_level": "CRITICAL",
                "risk_score": mid_conf,
                "confidence": mid_conf,
                "risk_categories": risks,
                "reasoning": f"Structural non-compliance regarding {theme}",
                "supporting_evidence": ["Evidence 1", "Evidence 2"],
                "execution_time_s": 1.5
            }
        }
    })
    
    # 12. trace_step (Resolution)
    trace.append({
        "event": "trace_step",
        "data": {
            "agent": "Resolution Generation",
            "agentColor": "#5AB0F0",
            "time": "2.1s",
            "query": None,
            "citations": None,
            "conclusion": {"summary": "Policy redesign required", "recommendation": recs},
            "severity": None,
            "confidence": None
        }
    })
    
    # 13. conflict_emitted
    conflict_payload = {
        "id": f"{scenario_name}_c1",
        "has_conflict": True,
        "title": f"{theme} Contradiction",
        "severity": "CRITICAL",
        "confidence": final_conf,
        "sources": [c["document"] for c in citations],
        "affected": ["Compliance", "IT Security"],
        "deadline": "24 days",
        "resolution": {"summary": "Policy redesign required", "recommendation": recs, "owners": ["Legal", "IT"]},
        "citations": citations,
        "risk_assessment": {
            "risk_level": "CRITICAL",
            "risk_score": mid_conf,
            "confidence": mid_conf,
            "risk_categories": risks,
            "reasoning": f"Structural non-compliance regarding {theme}",
            "supporting_evidence": ["Evidence 1", "Evidence 2"],
            "execution_time_s": 1.5
        }
    }
    trace.append({
        "event": "conflict_emitted",
        "data": conflict_payload
    })
    
    # 14. conflict_detected
    trace.append({
        "event": "conflict_detected",
        "data": conflict_payload
    })
    
    # 15. trace_step (Conflict Detection summary)
    trace.append({
        "event": "trace_step",
        "data": {
            "agent": "Conflict Detection",
            "agentColor": "#F09595",
            "time": "live",
            "query": None,
            "citations": None,
            "conclusion": f"Confirmed absolute contradiction regarding {theme}. {reqs}",
            "severity": "CRITICAL",
            "confidence": final_conf,
            "isSurprise": False
        }
    })
    
    # 16. complete
    trace.append({
        "event": "complete",
        "data": {
            "status": "complete",
            "total_conflicts": 1,
            "uncertain_count": 0,
            "blocked_count": 0,
            "is_mock_mode": True,
            "topics_analyzed": [theme],
            "execution_time_s": 6.1,
            "_meta": {"fallback": "DETERMINISTIC_FALLBACK"}
        }
    })
    
    return trace

scenarios = [
    {
        "name": "scenario_1_data_residency",
        "theme": "Data Residency and Processing",
        "conf": [65, 81, 93],
        "reqs": "IT mandates cloud centralization while Legal restricts cross-border data transfer.",
        "risks": ["Regulatory Violation", "Legal Exposure", "Fines"],
        "recs": ["Implement regional data partitioning", "Apply processing restrictions to European users", "Schedule an urgent compliance review"],
        "citations": [
            {"document": "IT_Policy.md", "section": "§3.1", "passage": "All data must be centralized in the US-East server.", "confidence": 0.95, "topic": "Data Residency"},
            {"document": "Privacy_Policy.md", "section": "§2.4", "passage": "European employee data cannot leave the EU.", "confidence": 0.98, "topic": "Data Residency"}
        ]
    },
    {
        "name": "scenario_2_anonymous_reporting",
        "theme": "Whistleblower Identity",
        "conf": [84, 91, 96],
        "reqs": "HR promises whistleblower anonymity, but IT mandates persistent identity logging on all networks.",
        "risks": ["Ethics Violation", "Employee Trust Failure", "Retaliation Risk"],
        "recs": ["Deploy an anonymized external reporting channel", "Implement IT exception handling for specific HR portals", "Introduce identity masking protocols"],
        "citations": [
            {"document": "HR_Handbook.md", "section": "§5.5", "passage": "All whistleblower reports are guaranteed absolute anonymity.", "confidence": 0.94, "topic": "Anonymity"},
            {"document": "IT_Security.md", "section": "§1.2", "passage": "All web traffic and form submissions must be logged to a user's Active Directory identity.", "confidence": 0.91, "topic": "Anonymity"}
        ]
    },
    {
        "name": "scenario_3_cross_border",
        "theme": "Cross-Border Access",
        "conf": [70, 80, 88],
        "reqs": "Security allows VPN access anywhere, but Export Control forbids access from embargoed regions.",
        "risks": ["Identity Management Failure", "Security Breach", "Export Control Fine"],
        "recs": ["Enforce location-based conditional access", "Audit regional restrictions", "Implement privileged access management barriers"],
        "citations": [
            {"document": "Remote_Work.md", "section": "§2", "passage": "Employees may connect via VPN from any country.", "confidence": 0.88, "topic": "Access"},
            {"document": "Export_Control.md", "section": "§7", "passage": "Access to internal networks from embargoed countries is strictly prohibited.", "confidence": 0.92, "topic": "Access"}
        ]
    },
    {
        "name": "scenario_4_vendor_compliance",
        "theme": "Vendor SLA Compliance",
        "conf": [71, 85, 89],
        "reqs": "Contracts guarantee 24/7 vendor access, but IT shuts down external access during internal audits.",
        "risks": ["Vendor Obligation Breach", "Contractual Gap", "Supply Chain Disruption"],
        "recs": ["Draft immediate contract amendments", "Review security attestations", "Perform supplier risk audit mapping"],
        "citations": [
            {"document": "Vendor_Contract.md", "section": "§4", "passage": "Vendor requires uninterrupted 24/7 access to the diagnostic API.", "confidence": 0.85, "topic": "Vendor Access"},
            {"document": "IT_Audit.md", "section": "§9", "passage": "All external API access is suspended during weekend security audits.", "confidence": 0.89, "topic": "Vendor Access"}
        ]
    },
    {
        "name": "scenario_5_nexora_demo",
        "theme": "Nexora Financial Governance",
        "conf": [75, 88, 95],
        "reqs": "A critical executive contradiction regarding identity logging and anonymity guarantees.",
        "risks": ["Impossible Requirements", "Executive Visibility Gap", "Policy Paralysis"],
        "recs": ["Escalate to executive committee", "Initiate emergency policy redesign", "Suspend conflicting procedures"],
        "citations": [
            {"document": "Nexora_Ethics.md", "section": "§1", "passage": "Anonymous reporting is a fundamental right of all Nexora staff.", "confidence": 0.96, "topic": "Nexora"},
            {"document": "Nexora_Compliance.md", "section": "§3", "passage": "Zero-trust architecture requires identity attribution for all internal tools.", "confidence": 0.94, "topic": "Nexora"}
        ]
    }
]

if __name__ == "__main__":
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    for s in scenarios:
        trace = build_scenario_json(
            s["name"], s["theme"], s["conf"][0], s["conf"][1], s["conf"][2], 
            s["reqs"], s["risks"], s["recs"], s["citations"]
        )
        
        out_path = DATA_DIR / f'{s["name"]}.json'
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(trace, f, indent=2)
            
        print(f"Built highly distinct scenario: {out_path.name}")
