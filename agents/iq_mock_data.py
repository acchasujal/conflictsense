"""
agents/iq_mock_data.py

Tier 3 pre-computed mock data for the Foundry IQ client and ConflictDetector.

Spec reference: docs/reliability_spec.md §1 (Tier 3 MOCK_MODE)
                docs/reasoning_trace_examples.md

Single responsibility: provide hardcoded mock responses for when Azure is
unavailable. Zero business logic — only lookup tables and factory functions.

This module is imported by:
  - agents/foundry_iq_client.py  (document-level citation mocks)
  - agents/conflict_detector.py  (conflict detection mocks)
"""

from __future__ import annotations

# ─── Foundry IQ Document Citation Mocks ──────────────────────────────────────
# Keyed by (document_filename, topic_key).
# topic_key is produced by topic_key_for() below.

MOCK_CITATIONS: dict[tuple[str, str], list[dict]] = {
    # topic: "data location"
    ("IT_Security_Policy.md", "data location"): [{
        "section": "§4.2",
        "passage": "All company data processing shall occur exclusively on US-domiciled servers. VPN access restricted to US IP ranges.",
        "confidence": 0.96,
    }],
    ("HR_Remote_Work_Policy.md", "data location"): [{
        "section": "§2.1",
        "passage": "Employees may work from any global location without prior approval.",
        "confidence": 0.95,
    }],
    ("DPDP_Compliance_Directive.md", "data location"): [{
        "section": "§3.1",
        "passage": "Personal data of Indian-resident employees must be processed within Indian jurisdiction. Effective July 1, 2026.",
        "confidence": 0.94,
    }],
    ("Data_Governance_Policy.md", "data location"): [{
        "section": "§7.3",
        "passage": "EU employee data subject to GDPR residency requirements.",
        "confidence": 0.74,
    }],
    # topic: "anonymity"
    ("Whistleblower_Policy.md", "anonymity"): [{
        "section": "§4.2",
        "passage": "Reports filed through the ethics portal are anonymous. Employee identity is never logged or traceable by any internal party.",
        "confidence": 0.91,
    }],
    ("IT_Security_Policy.md", "anonymity"): [{
        "section": "§12.1",
        "passage": "All system access is logged with full user identity for security audit purposes. No exceptions permitted.",
        "confidence": 0.95,
    }],
    # topic: "vacation policy"
    ("Employee_Handbook.md", "vacation policy"): [{
        "section": "§5.1",
        "passage": "All employees are entitled to 20 vacation days per calendar year.",
        "confidence": 0.80,
    }],
    ("HR_Remote_Work_Policy.md", "vacation policy"): [{
        "section": "§7.2",
        "passage": "Annual leave entitlement is 20 working days per year for all staff.",
        "confidence": 0.78,
    }],
}

SILENT_DOCS_BY_TOPIC: dict[str, set[str]] = {
    "data location": {
        "Whistleblower_Policy.md",
        "Employee_Handbook.md",
        "Finance_Expense_Policy.md",
    },
    "anonymity": {
        "HR_Remote_Work_Policy.md",
        "Data_Governance_Policy.md",
        "DPDP_Compliance_Directive.md",
        "Employee_Handbook.md",
        "Finance_Expense_Policy.md",
    },
}


# ─── Conflict Detection Mocks ─────────────────────────────────────────────────
# Keyed by topic_key. Exact prose from docs/reasoning_trace_examples.md.

_CONFLICT_MOCKS: dict[str, dict] = {
    "anonymity": {
        "has_conflict": True,
        "conflict_pairs": [{
            "document_a": "Whistleblower_Policy.md", "section_a": "§4.2",
            "document_b": "IT_Security_Policy.md",   "section_b": "§12.1",
            "conflict_type": "Direct Contradiction",
            "why_impossible": (
                "The Whistleblower Policy guarantees that a report submitted through "
                "the ethics portal is anonymous — employee identity is never logged or "
                "traceable. The IT Security Policy requires all system access to be "
                "logged with full user identity, with no exceptions permitted. A report "
                "filed through the ethics portal is a system access event. That event "
                "cannot be both identity-logged and anonymous simultaneously."
            ),
        }],
        "reasoning": (
            "Nexora's Whistleblower Policy makes a legal commitment to every employee: "
            "your report cannot be traced. Its IT Security Policy makes a technical "
            "commitment: every system action is logged with user identity, no exceptions. "
            "These two statements cannot simultaneously be true. Every report filed through "
            "the ethics portal is traceable — full stop. The anonymity guarantee exists "
            "on paper. It does not exist in the system."
        ),
        "severity": "CRITICAL", "confidence": 0.91, "is_surprise": True,
    },
    "data location": {
        "has_conflict": True,
        "conflict_pairs": [{
            "document_a": "IT_Security_Policy.md",        "section_a": "§4.2",
            "document_b": "HR_Remote_Work_Policy.md",     "section_b": "§2.1",
            "document_c": "DPDP_Compliance_Directive.md", "section_c": "§3.1",
            "conflict_type": "Data Residency Conflict",
            "why_impossible": (
                "IT Security mandates US servers. The DPDP Directive requires Indian "
                "servers for Indian-resident employees. HR policy permits those same "
                "employees to work from anywhere — which means their data is processed "
                "wherever they sit. These rules apply to the same employee population "
                "simultaneously. They cannot all be satisfied."
            ),
        }],
        "reasoning": (
            "IT Security mandates US servers. The DPDP Directive requires Indian servers "
            "for Indian-resident employees. HR policy permits those same employees to work "
            "from anywhere — which means their data is processed wherever they sit. All "
            "three rules apply to the same employee population simultaneously. They cannot all be "
            "satisfied. This is not ambiguity or edge-case overlap. It is a structural "
            "impossibility baked into the current architecture."
        ),
        "severity": "CRITICAL", "confidence": 0.96, "is_surprise": False,
    },
    "incident reporting": {
        "has_conflict": True,
        "conflict_pairs": [{
            "document_a": "IT_Security_Policy.md",  "section_a": "§9.1",
            "document_b": "Whistleblower_Policy.md", "section_b": "§4.2",
            "conflict_type": "Approval Workflow Conflict",
            "why_impossible": (
                "IT Security Policy requires security incidents to be reported to the "
                "CISO within 72 hours to comply with FCA mandates. The Whistleblower "
                "Policy routes regulatory non-compliance reports exclusively to the "
                "Legal Compliance Committee on a monthly review cycle, explicitly "
                "bypassing IT reporting lines. An employee who discovers a regulatory "
                "breach and reports it through the whistleblower channel satisfies one "
                "obligation but automatically violates the other."
            ),
        }],
        "reasoning": (
            "The IT Security Policy mandates that security incidents reach the CISO within "
            "72 hours — a hard FCA regulatory requirement. The Whistleblower Policy routes "
            "all reports of regulatory non-compliance exclusively to the Legal Compliance "
            "Committee on a monthly cycle, explicitly bypassing IT security lines. For any "
            "employee who discovers a security breach and reports it as a regulatory "
            "compliance failure, these two obligations fire simultaneously — and they point "
            "in opposite directions. The 72-hour FCA window will expire before the monthly "
            "Legal Committee even convenes."
        ),
        "severity": "CRITICAL", "confidence": 0.88, "is_surprise": False,
    },
    "byod": {
        "has_conflict": True,
        "conflict_pairs": [{
            "document_a": "IT_Security_Policy.md",     "section_a": "§6.3",
            "document_b": "Data_Governance_Policy.md", "section_b": "§11.2",
            "conflict_type": "Retention Conflict",
            "why_impossible": (
                "IT Security requires immediate and permanent deletion of company data "
                "from personal devices upon termination. Data Governance requires all "
                "employee communications and work products to be retained for 7 years. "
                "Both obligations trigger at the same instant for the same data."
            ),
        }],
        "reasoning": (
            "The IT Security Policy mandates immediate, permanent deletion of company data "
            "from personal devices at the moment of termination or transfer. The Data "
            "Governance Policy simultaneously requires that all employee communications and "
            "work products be retained for 7 years. Both obligations trigger at the same "
            "instant for the same data on the same device. Deletion makes retention "
            "impossible. Retention makes deletion impossible."
        ),
        "severity": "HIGH", "confidence": 0.83, "is_surprise": False,
    },
    "relocation": {
        "has_conflict": True,
        "conflict_pairs": [{
            "document_a": "Employee_Handbook.md",      "section_a": "§8.3",
            "document_b": "Finance_Expense_Policy.md", "section_b": "§5.1",
            "conflict_type": "Approval Workflow Conflict",
            "why_impossible": (
                "The Employee Handbook grants an automatic $5,000 relocation allowance "
                "disbursed in the first payroll cycle. The Finance Policy states that all "
                "relocation disbursements are discretionary and require prior written "
                "authorization from the Finance Director. An employee relocated today is "
                "simultaneously owed an automatic payment and prohibited from receiving "
                "one without approval that has not been sought."
            ),
        }],
        "reasoning": (
            "The Employee Handbook creates a legal entitlement: relocation automatically "
            "triggers a $5,000 disbursement in the next payroll run. The Finance Expense "
            "Policy makes all relocation disbursements conditional on prior written Finance "
            "Director authorization. Either the entitlement is automatic — in which case "
            "Finance Policy is violated — or it requires authorization — in which case every "
            "relocation processed without pre-approval breaches the Handbook."
        ),
        "severity": "HIGH", "confidence": 0.79, "is_surprise": False,
    },
    "software procurement": {
        "has_conflict": True,
        "conflict_pairs": [{
            "document_a": "Finance_Expense_Policy.md", "section_a": "§3.1",
            "document_b": "IT_Security_Policy.md",     "section_b": "§11.4",
            "conflict_type": "Approval Workflow Conflict",
            "why_impossible": (
                "Finance Policy grants department managers unilateral authority to approve "
                "SaaS purchases under $5,000. IT Security Policy requires all software — "
                "regardless of cost — to undergo formal IT Security risk assessment. A "
                "manager who exercises their Finance authority on a $500 SaaS subscription "
                "has simultaneously violated IT Security Policy."
            ),
        }],
        "reasoning": (
            "Finance Policy explicitly grants department managers autonomous procurement "
            "authority for software under $5,000. IT Security Policy explicitly states all "
            "software must pass IT Security assessment before procurement, with no cost-based "
            "threshold. Every sub-$5,000 SaaS purchase made under Finance Policy authority "
            "is simultaneously non-compliant with IT Security Policy."
        ),
        "severity": "MEDIUM", "confidence": 0.77, "is_surprise": False,
    },
    "data minimization": {
        "has_conflict": True,
        "conflict_pairs": [{
            "document_a": "Data_Governance_Policy.md", "section_a": "§3",
            "document_b": "Employee_Handbook.md",      "section_b": "§20",
            "conflict_type": "Retention Conflict",
            "why_impossible": (
                "Data Governance mandates destruction of employee personal records 12 months "
                "post-employment. The Employee Handbook states training logs and performance "
                "reviews are retained indefinitely. These are the same records — one policy "
                "requires destruction, the other requires indefinite retention."
            ),
        }],
        "reasoning": (
            "The Data Governance Policy mandates that employee personal records and "
            "performance evaluations be destroyed 12 months after employment ends. The "
            "Employee Handbook states that training logs, performance reviews, and "
            "compliance records are retained indefinitely. One says destroy. The other "
            "says keep. There is no reading of either policy that makes both simultaneously "
            "compliant."
        ),
        "severity": "MEDIUM", "confidence": 0.74, "is_surprise": False,
    },
    "mfa": {
        "has_conflict": True,
        "conflict_pairs": [{
            "document_a": "IT_Security_Policy.md",  "section_a": "§7",
            "document_b": "HR_Remote_Work_Policy.md", "section_b": "§4",
            "conflict_type": "Access Control Conflict",
            "why_impossible": (
                "IT Security Policy mandates MFA for all access with no exceptions for "
                "any user type. HR Remote Work Policy permits department managers to grant "
                "contractors network access without MFA. A manager who grants a contractor "
                "MFA-free access under HR Remote Work §4 has simultaneously violated IT "
                "Security Policy §7."
            ),
        }],
        "reasoning": (
            "IT Security Policy §7 mandates MFA for all users with zero exceptions. HR "
            "Remote Work Policy §4 grants department managers the authority to waive MFA "
            "for contractors with written approval. IT Security eliminates the exception "
            "authority that HR creates. Any manager who exercises the HR-granted exception "
            "is simultaneously in violation of the IT Security mandate."
        ),
        "severity": "MEDIUM", "confidence": 0.71, "is_surprise": False,
    },
    "expense reimbursement": {
        "has_conflict": True,
        "conflict_pairs": [{
            "document_a": "Finance_Expense_Policy.md", "section_a": "§8",
            "document_b": "Employee_Handbook.md",      "section_b": "§22",
            "conflict_type": "Direct Contradiction",
            "why_impossible": (
                "Finance Policy strictly prohibits all self-certification of expenses with "
                "no exceptions. The Employee Handbook explicitly permits self-certification "
                "for emergency expenses under $100. An employee who self-certifies a $50 "
                "emergency expense has complied with the Handbook and violated Finance "
                "Policy simultaneously."
            ),
        }],
        "reasoning": (
            "Finance Expense Policy §8 states that self-certification of expenses is "
            "strictly prohibited, with no qualifier. Employee Handbook §22 creates a "
            "specific carve-out permitting self-certification for emergency expenses under "
            "$100. Finance says never. The Handbook says sometimes. An employee following "
            "the Handbook for a $50 emergency purchase is simultaneously violating Finance "
            "Policy."
        ),
        "severity": "MEDIUM", "confidence": 0.68, "is_surprise": False,
    },
    "vacation policy": {
        # NOT a conflict: both policies grant 20 days; terminology differs (vacation vs annual
        # leave) but the entitlement is identical. This is the canonical negative test case per
        # test_corpus.md §2. Confidence is 0.0 — no structural impossibility exists.
        "has_conflict": False,
        "conflict_pairs": [],
        "reasoning": (
            "The Employee Handbook specifies '20 vacation days' and the HR Remote Work "
            "Policy specifies '20 working days of annual leave'. The entitlement is "
            "identical; only the terminology differs. Both policies can be satisfied "
            "simultaneously. This is a wording difference, not a structural conflict."
        ),
        "severity": None, "confidence": 0.0, "is_surprise": False,
    },
}

# ─── Impact Mocks (Phase 3) ───────────────────────────────────────────────────

IMPACT_MOCKS: dict[str, str] = {
    "anonymity": "Affects whistleblower reports submitted through the ethics portal; identity exposure risk is supported by the logging citation.",
    "data location": "Affects employees in Bangalore referenced by the residency scenario. Specific penalties are not quantified without grounded regulatory evidence.",
    "incident reporting": "Affects security incident routing. Regulatory exposure may exist, but fines are not quantified without grounded regulatory evidence.",
    "byod": "Affects 450 BYOD users. Retention failure risk vs. Data breach risk.",
    "relocation": "Affects 12 planned relocations this quarter ($60,000 pending).",
    "software procurement": "Affects manager-level SaaS purchases where Finance approval and IT Security review obligations conflict.",
    "data minimization": "Affects all departed employees. GDPR violation risk vs HR records gap.",
    "mfa": "Affects 85 active contractors. Direct pathway for credential stuffing attacks.",
    "expense reimbursement": "Affects approx 200 emergency expenses annually. Minor financial risk, moderate audit risk.",
    "vacation policy": "Affects 0 employees. No operational impact (semantic difference only).",
}


# ─── Topic Key Mapping ─────────────────────────────────────────────────────────

def topic_key_for(topic: str) -> str:
    """Map a free-form topic string to a canonical mock key."""
    t = topic.lower()
    # Scenario 2: Whistleblower anonymity
    if any(w in t for w in ["anonymity", "anonymous", "reporting channel", "whistleblower"]):
        return "anonymity"
    # Scenario 2: IT audit logging (second topic)
    if any(w in t for w in ["audit logging", "identity tracking", "user identity", "access log"]):
        return "mfa"  # re-uses the access control mock (distinct from anonymity)
    # Scenario 1: Data location / residency
    if any(w in t for w in ["data location", "processing", "residency", "server"]):
        return "data location"
    # Scenario 1: Remote work geo restrictions (second topic)
    if any(w in t for w in ["geographic restriction", "vpn policy", "geo restriction"]):
        return "incident reporting"  # distinct conflict: CISO 72h vs whistleblower routing
    # Scenario 3: BYOD deletion
    if any(w in t for w in ["byod", "deletion", "device"]):
        return "byod"
    # Scenario 3: Remote work security / device compliance
    if any(w in t for w in ["device compliance", "remote work security", "remote security"]):
        return "data minimization"  # distinct: retention conflict
    # Scenario 4: Expense approval
    if any(w in t for w in ["expense", "receipt", "reimbursement", "financial approval"]):
        return "relocation"  # approval chain conflict
    # Scenario 4: Software procurement
    if any(w in t for w in ["software", "saas", "procurement", "authorization"]):
        return "software procurement"
    # General fallbacks
    if any(w in t for w in ["incident", "breach", "fca", "72"]):
        return "incident reporting"
    if any(w in t for w in ["relocation", "allowance"]):
        return "relocation"
    if any(w in t for w in ["minimization", "minimisation", "retention"]):
        return "data minimization"
    if any(w in t for w in ["mfa", "multi-factor", "authentication"]):
        return "mfa"
    if any(w in t for w in ["vacation", "leave", "pto"]):
        return "vacation policy"
    return t


# ─── Public Factory Functions ─────────────────────────────────────────────────

def get_conflict_mock_response(topic: str) -> dict:
    """
    Return the pre-computed Tier 3 conflict detection response for a topic.
    Never raises — guaranteed to return a valid dict.
    """
    key = topic_key_for(topic)
    mock = _CONFLICT_MOCKS.get(key)
    if mock:
        return {
            "has_conflict": mock["has_conflict"],
            "conflict_pairs": mock["conflict_pairs"],
            "reasoning": mock["reasoning"],
            "severity": mock["severity"],
            "confidence": mock["confidence"],
            "is_surprise": mock.get("is_surprise", False),
        }
    return {
        "has_conflict": False, "conflict_pairs": [],
        "reasoning": "No pre-computed response available for this topic.",
        "severity": None, "confidence": 0.0,
    }
