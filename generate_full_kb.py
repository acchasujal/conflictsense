import json
import uuid

# Load base template
with open('data/precomputed/scenario_5_nexora_demo.json', 'r') as f:
    data = json.load(f)

# The goal is to make full_kb_analysis distinct.
# Let's change the steps and conflicts.

conflicts = [
    {
        "id": "C-" + str(uuid.uuid4())[:8],
        "title": "Expense Policy vs Procurement Limits",
        "severity": "CRITICAL",
        "confidence": 98,
        "description": "Global Expense Policy allows managers to approve up to $10,000 in software purchases, but the Procurement Master Agreement strictly limits unvetted software purchases to $500 to prevent shadow IT.",
        "affected": {
            "teams": ["Finance", "IT", "All Managers"],
            "systems": ["Concur", "Procurement Portal"]
        },
        "deadline": "Immediate",
        "resolution": {
            "summary": "Reconcile approval limits. Route software >$500 through IT procurement.",
            "recommendation": "Update Expense Policy Section 4 to explicitly carve out software and refer to Procurement Agreement.",
            "owners": ["CFO", "CIO"]
        },
        "risk_assessment": {
            "financial_exposure": 500000,
            "potential_consequences": ["Unmanaged Shadow IT", "Data breaches from unvetted vendors", "Budget overruns"]
        },
        "evidence": [
            {
                "document": "Global Expense Policy.pdf",
                "section": "§4. Approvals",
                "passage": "Managers hold discretionary approval authority for operational expenses up to $10,000.",
                "confidence": 0.99
            },
            {
                "document": "Procurement Master Agreement.docx",
                "section": "§2. Software",
                "passage": "All software purchases exceeding $500 must undergo IT Security review and formal procurement. No exceptions.",
                "confidence": 0.99
            }
        ]
    },
    {
        "id": "C-" + str(uuid.uuid4())[:8],
        "title": "Data Retention vs Remote Work Storage",
        "severity": "HIGH",
        "confidence": 95,
        "description": "Data Retention Policy requires all customer data to be purged after 3 years, but Remote Work Guidelines allow employees to use local offline backups indefinitely.",
        "affected": {
            "teams": ["Legal", "HR", "IT"],
            "systems": ["Local Drives", "Cloud Storage"]
        },
        "deadline": "30 Days",
        "resolution": {
            "summary": "Ban permanent local backups of customer data.",
            "recommendation": "Update Remote Work Guidelines to enforce 30-day auto-wipes on local offline customer data.",
            "owners": ["CISO"]
        },
        "risk_assessment": {
            "financial_exposure": 1200000,
            "potential_consequences": ["GDPR Violations", "Stale data leaks from stolen laptops"]
        },
        "evidence": [
            {
                "document": "Data Retention Policy.md",
                "section": "§3. Purging",
                "passage": "Customer PII must be irrecoverably purged after 3 years.",
                "confidence": 0.95
            },
            {
                "document": "Remote Work Guidelines.pdf",
                "section": "§1. Offline Access",
                "passage": "Employees may maintain local offline copies of necessary files to ensure productivity during outages.",
                "confidence": 0.95
            }
        ]
    },
    {
        "id": "C-" + str(uuid.uuid4())[:8],
        "title": "Contractor Access vs Zero Trust Mandate",
        "severity": "HIGH",
        "confidence": 90,
        "description": "Vendor Management Policy grants vendors VPN access, but Zero Trust Architecture restricts all external access to specific application proxies.",
        "affected": {
            "teams": ["Vendor Management", "Security"],
            "systems": ["VPN", "Identity Provider"]
        },
        "deadline": "60 Days",
        "resolution": {
            "summary": "Deprecate vendor VPNs.",
            "recommendation": "Migrate all vendors to Zero Trust Application Access.",
            "owners": ["VP Security"]
        },
        "risk_assessment": {
            "financial_exposure": 800000,
            "potential_consequences": ["Lateral movement by compromised vendors", "Audit failures"]
        },
        "evidence": [
            {
                "document": "Vendor Management Policy.docx",
                "section": "§5. Access",
                "passage": "Vendors will be issued standard VPN profiles for internal network access.",
                "confidence": 0.90
            },
            {
                "document": "Zero Trust Architecture.md",
                "section": "§2. External Entities",
                "passage": "External entities shall never be granted VPN access. All access must be app-specific via the Zero Trust gateway.",
                "confidence": 0.98
            }
        ]
    }
]

# Create a brand new trace specifically for this
new_trace = []
for i in range(5):
    new_trace.append({
        "agent": "Document Analysis",
        "action": "Parsing Corporate Policies",
        "details": f"Extracting clauses from document batch {i+1}",
        "duration_ms": 150 + i * 10
    })

new_trace.append({
    "agent": "Conflict Detection",
    "action": "Cross-referencing 500+ clauses",
    "details": "Checking for structural contradictions across Finance, HR, IT, and Legal.",
    "duration_ms": 850
})

for idx, c in enumerate(conflicts):
    new_trace.append({
        "agent": "Conflict Detection",
        "action": f"Detected: {c['title']}",
        "severity": c['severity'],
        "duration_ms": 120
    })
    new_trace.append({
        "agent": "Conflict Validation",
        "action": f"Validating {c['title']}",
        "citations": c['evidence'],
        "confidence": c['confidence'],
        "duration_ms": 300,
        "conclusion": f"Validated strict contradiction regarding {c['title']}."
    })
    new_trace.append({
        "agent": "Risk Quantification",
        "action": "Assessing Enterprise Impact",
        "severity": c['severity'],
        "confidence": c['confidence'],
        "duration_ms": 250,
        "conclusion": c['risk_assessment']
    })
    new_trace.append({
        "agent": "Resolution Generation",
        "action": "Drafting Remediation",
        "duration_ms": 400,
        "conclusion": c['resolution']
    })
    # Final conflict record
    new_trace.append({
        "agent": "System",
        "action": "Conflict Published",
        "conflict_record": c
    })

new_trace.append({
    "agent": "System",
    "action": "Enterprise Audit Complete",
    "details": f"Processed 7 documents. Found {len(conflicts)} critical/high conflicts.",
    "duration_ms": 50,
    "conclusion": {
        "summary": "Enterprise Audit detected multiple high-risk compliance gaps across Finance, IT, and Legal.",
        "recommendation": "Immediate attention required from CFO and CISO."
    }
})

with open('data/precomputed/full_kb_analysis.json', 'w') as f:
    json.dump(new_trace, f, indent=2)

print("Generated full_kb_analysis.json with", len(new_trace), "steps and", len(conflicts), "unique conflicts.")
