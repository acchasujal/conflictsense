/**
 * frontend/src/lib/mockData.js
 *
 * Tier 3 pre-computed mock data — no API, no Azure, no backend dependency.
 * All arrays are sourced from mock_data/ JSON files (via Vite's static asset
 * resolution of ?url imports or inline JSON imports).
 *
 * Spec reference: docs/reliability_spec.md §1 (Tier 3 MOCK_MODE)
 *                 docs/data_contracts.md
 */

// Vite resolves ?url for JSON files as static assets; for inline data we
// define them here directly to avoid any fetch — zero network dependency.
//
// CANONICAL SOURCE: mock_data/precomputed_trace.json
// CANONICAL SOURCE: mock_data/precomputed_conflicts.json
// CANONICAL SOURCE: mock_data/documents.json

export const MOCK_DOCUMENTS = [
  {
    id: 1,
    name: "IT_Security_Policy.md",
    dept: "IT Infrastructure",
    date: "Jan 2024",
    size: "18 KB",
    foundry_iq_source_id: "src_it_security_policy",
  },
  {
    id: 2,
    name: "HR_Remote_Work_Policy.md",
    dept: "Human Resources",
    date: "Mar 2025",
    size: "12 KB",
    foundry_iq_source_id: "src_hr_remote_work_policy",
  },
  {
    id: 3,
    name: "Data_Governance_Policy.md",
    dept: "Legal & Compliance",
    date: "Nov 2023",
    size: "22 KB",
    foundry_iq_source_id: "src_data_governance_policy",
  },
  {
    id: 4,
    name: "Employee_Handbook.md",
    dept: "Human Resources",
    date: "Feb 2024",
    size: "41 KB",
    foundry_iq_source_id: "src_employee_handbook",
  },
  {
    id: 5,
    name: "Whistleblower_Policy.md",
    dept: "Legal & Compliance",
    date: "Aug 2023",
    size: "9 KB",
    foundry_iq_source_id: "src_whistleblower_policy",
  },
  {
    id: 6,
    name: "Finance_Expense_Policy.md",
    dept: "Finance",
    date: "Jun 2024",
    size: "14 KB",
    foundry_iq_source_id: "src_finance_expense_policy",
  },
  {
    id: 7,
    name: "DPDP_Compliance_Directive.md",
    dept: "Legal & Compliance",
    date: "May 2026",
    size: "7 KB",
    isNew: true,
    foundry_iq_source_id: "src_dpdp_compliance_directive",
  },
];

// Canonical trace steps — exact prose from docs/reasoning_trace_examples.md
// Agent colors: DocumentAnalyzer=#85B7EB ConflictDetector=#F09595
//               ImpactAssessor=#5DCAA5  RiskQuantifier=#FAC775
//               ResolutionRecommender=#9FE1CB
export const MOCK_TRACE_STEPS = [
  {
    agent: "DocumentAnalyzer",
    agentColor: "#85B7EB",
    time: "0.3s",
    query: "employee data location and processing rules",
    citations: [
      {
        document: "IT_Security_Policy.md",
        section: "§4.2",
        passage:
          "All company data processing shall occur exclusively on US-domiciled servers. VPN access restricted to US IP ranges.",
        confidence: 0.96,
        topic: "employee data location and processing rules",
      },
      {
        document: "HR_Remote_Work_Policy.md",
        section: "§2.1",
        passage: "Employees may work from any global location without prior approval.",
        confidence: 0.95,
        topic: "employee data location and processing rules",
      },
      {
        document: "DPDP_Compliance_Directive.md",
        section: "§3.1",
        passage:
          "Personal data of Indian-resident employees must be processed within Indian jurisdiction. Effective July 1, 2026.",
        confidence: 0.94,
        topic: "employee data location and processing rules",
      },
      {
        document: "Data_Governance_Policy.md",
        section: "§7.3",
        passage: "EU employee data subject to GDPR residency requirements.",
        confidence: 0.74,
        topic: "employee data location and processing rules",
      },
    ],
    conclusion: null,
    severity: null,
    confidence: null,
  },
  {
    agent: "ConflictDetector",
    agentColor: "#F09595",
    time: "0.8s",
    query: null,
    citations: null,
    conclusion:
      "IT Security mandates US servers. The DPDP Directive requires Indian servers for Indian-resident employees. HR policy permits those same employees to work from anywhere — which means their data is processed wherever they sit. All three rules apply to the same 34 employees simultaneously. They cannot all be satisfied. This is not ambiguity or edge-case overlap. It is a structural impossibility baked into the current architecture.",
    severity: "CRITICAL",
    confidence: 96,
  },
  {
    agent: "ImpactAssessor",
    agentColor: "#5DCAA5",
    time: "1.1s",
    query: null,
    citations: null,
    conclusion:
      "34 employees in India-based roles currently fall in the non-compliant zone. Affected systems: primary VPN gateway, US East data pipelines. Affected teams: IT Infrastructure (server provisioning owner), HR (policy amendment owner), Legal (regulatory response). Regulatory deadline: July 1, 2026 — 24 days from today.",
    severity: null,
    confidence: null,
  },
  {
    agent: "RiskQuantifier",
    agentColor: "#FAC775",
    time: "1.4s",
    query: null,
    citations: null,
    conclusion:
      "Regulatory risk: HIGH. DPDP Act §91 — penalties up to ₹250 crore for systemic non-compliance. Operational risk: MEDIUM — India-region server provisioning requires 2–4 week lead time, which conflicts with the deadline if not started immediately. Legal exposure: HIGH — ongoing violation from July 1 if architecture is unchanged. Reputational risk: MEDIUM — regulatory enforcement actions are public record in India.",
    severity: null,
    confidence: null,
  },
  {
    agent: "DocumentAnalyzer",
    agentColor: "#85B7EB",
    time: "1.9s",
    query: "employee reporting channels and anonymity guarantees",
    citations: [
      {
        document: "Whistleblower_Policy.md",
        section: "§4.2",
        passage:
          "Reports filed through the ethics portal are anonymous. Employee identity is never logged or traceable by any internal party.",
        confidence: 0.91,
        topic: "employee reporting channels and anonymity guarantees",
      },
      {
        document: "IT_Security_Policy.md",
        section: "§12.1",
        passage:
          "All system access is logged with full user identity for security audit purposes. No exceptions permitted.",
        confidence: 0.95,
        topic: "employee reporting channels and anonymity guarantees",
      },
    ],
    conclusion: null,
    severity: null,
    confidence: null,
  },
  {
    agent: "ConflictDetector",
    agentColor: "#F09595",
    time: "2.3s",
    query: null,
    citations: null,
    conclusion:
      "Nexora's Whistleblower Policy makes a legal commitment to every employee: your report cannot be traced. Its IT Security Policy makes a technical commitment: every system action is logged with user identity, no exceptions. These two statements cannot simultaneously be true. Every report filed through the ethics portal is traceable — full stop. The anonymity guarantee exists on paper. It does not exist in the system.",
    severity: "CRITICAL",
    confidence: 91,
    isSurprise: true,
  },
  {
    agent: "ResolutionRecommender",
    agentColor: "#9FE1CB",
    time: "2.7s",
    query: null,
    citations: null,
    conclusion:
      "Analysis complete. 9 conflicts detected across 7 policy documents — 3 Critical, 2 High, 4 Medium. Prioritised resolution roadmap generated with owner assignments and deadlines. All findings are pending human review. No autonomous action has been taken or will be taken without explicit approval.",
    severity: null,
    confidence: null,
  },
];

// Canonical conflict records — 9 total, exact titles/severities/confidence
// from docs/data_contracts.md §2 and canonical UI source
export const MOCK_CONFLICTS = [
  {
    id: "1",
    has_conflict: true,
    title: "Data residency: three-way structural impossibility",
    severity: "CRITICAL",
    confidence: 96,
    sources: [
      "IT_Security_Policy.md §4.2",
      "HR_Remote_Work_Policy.md §2.1",
      "DPDP_Compliance_Directive.md §3.1",
    ],
    affected: "34 India-based employees · IT Infrastructure · Legal",
    deadline: "July 1, 2026 — 24 days",
    resolution:
      "Option A (recommended): Provision India-region Azure servers — Owner: CTO, Deadline: June 28. Option B: Temporary travel restriction for India-resident staff — Owner: CHRO, Deadline: June 25.",
    citations: [
      {
        document: "IT_Security_Policy.md",
        section: "§4.2",
        passage:
          "All company data processing shall occur exclusively on US-domiciled servers. VPN access restricted to US IP ranges.",
        confidence: 0.96,
        topic: "employee data location and processing rules",
      },
      {
        document: "HR_Remote_Work_Policy.md",
        section: "§2.1",
        passage: "Employees may work from any global location without prior approval.",
        confidence: 0.95,
        topic: "employee data location and processing rules",
      },
      {
        document: "DPDP_Compliance_Directive.md",
        section: "§3.1",
        passage:
          "Personal data of Indian-resident employees must be processed within Indian jurisdiction. Effective July 1, 2026.",
        confidence: 0.94,
        topic: "employee data location and processing rules",
      },
    ],
  },
  {
    id: "2",
    has_conflict: true,
    title: "Anonymity guarantee is technically impossible",
    severity: "CRITICAL",
    confidence: 91,
    sources: ["Whistleblower_Policy.md §4.2", "IT_Security_Policy.md §12.1"],
    affected: "All employees · Legal & Compliance · IT Security",
    deadline: null,
    resolution:
      "Migrate ethics portal to off-system anonymous channel (e.g., third-party hotline) OR carve IT logging exceptions for ethics portal access. Requires Legal + IT Security Director alignment.",
    isSurprise: true,
    citations: [
      {
        document: "Whistleblower_Policy.md",
        section: "§4.2",
        passage:
          "Reports filed through the ethics portal are anonymous. Employee identity is never logged or traceable by any internal party.",
        confidence: 0.91,
        topic: "employee reporting channels and anonymity guarantees",
      },
      {
        document: "IT_Security_Policy.md",
        section: "§12.1",
        passage:
          "All system access is logged with full user identity for security audit purposes. No exceptions permitted.",
        confidence: 0.95,
        topic: "employee reporting channels and anonymity guarantees",
      },
    ],
  },
  {
    id: "3",
    has_conflict: true,
    title: "Incident reporting: parallel obligation gap",
    severity: "CRITICAL",
    confidence: 88,
    sources: ["IT_Security_Policy.md §9.1", "Whistleblower_Policy.md §4.2"],
    affected: "All staff · IT Security · Legal · FCA compliance",
    deadline: "FCA 72-hour breach notification window",
    resolution:
      "Add clause to Whistleblower Policy: security incidents require parallel internal IT Security notification within 2 hours, regardless of external reporting channel used.",
    citations: [
      {
        document: "IT_Security_Policy.md",
        section: "§9.1",
        passage:
          "Security incidents must be reported internally to the CISO within 72 hours to comply with FCA regulatory reporting mandates. No external whistleblowing reports are processed by security.",
        confidence: 0.88,
        topic: "security incident reporting timelines",
      },
      {
        document: "Whistleblower_Policy.md",
        section: "§4.2",
        passage:
          "Whistleblower reports regarding regulatory non-compliance are routed exclusively to the Legal Compliance Committee, with review cycles occurring on a monthly basis, bypassing standard IT reporting lines.",
        confidence: 0.85,
        topic: "security incident reporting timelines",
      },
    ],
  },
  {
    id: "4",
    has_conflict: true,
    title: "BYOD deletion vs. 7-year retention conflict",
    severity: "HIGH",
    confidence: 83,
    sources: ["IT_Security_Policy.md §6.3", "Data_Governance_Policy.md §11.2"],
    affected: "BYOD users · IT · Legal · Compliance",
    deadline: null,
    resolution:
      "Prohibit storage of sensitive data categories on personal devices — eliminates both obligations simultaneously. Amend IT Security Policy §6.3 with prohibited data type list.",
    citations: [
      {
        document: "IT_Security_Policy.md",
        section: "§6.3",
        passage:
          "Upon termination or transfer, all company data stored on personal devices (BYOD) must be immediately and permanently deleted.",
        confidence: 0.83,
        topic: "BYOD data deletion and retention rules",
      },
      {
        document: "Data_Governance_Policy.md",
        section: "§11.2",
        passage:
          "To comply with financial audits, all communications and work products of employees must be retained for a mandatory period of 7 years.",
        confidence: 0.82,
        topic: "BYOD data deletion and retention rules",
      },
    ],
  },
  {
    id: "5",
    has_conflict: true,
    title: "Compensation entitlement: automatic vs. discretionary",
    severity: "HIGH",
    confidence: 79,
    sources: ["Employee_Handbook.md §8.3", "Finance_Expense_Policy.md §5.1"],
    affected: "12 employees currently in qualifying situations · HR · Finance",
    deadline: null,
    resolution:
      "Amend Handbook §8.3 to require Finance Director pre-approval, OR Finance Policy §5.1 to recognize automatic entitlements. Requires HR and Finance Director alignment.",
    citations: [
      {
        document: "Employee_Handbook.md",
        section: "§8.3",
        passage:
          "Employees relocated to regional offices are automatically entitled to a standard relocation allowance of $5,000, disbursed in the first payroll cycle.",
        confidence: 0.79,
        topic: "relocation and expense compensation",
      },
      {
        document: "Finance_Expense_Policy.md",
        section: "§5.1",
        passage:
          "All relocation expenses and allowance disbursements are discretionary and require prior written authorization from the Finance Director before any commitment is made.",
        confidence: 0.78,
        topic: "relocation and expense compensation",
      },
    ],
  },
  {
    id: "6",
    has_conflict: true,
    title: "Software procurement: approval authority gap",
    severity: "MEDIUM",
    confidence: 77,
    sources: ["Finance_Expense_Policy.md §3.1", "IT_Security_Policy.md §11.4"],
    affected: "All departments · IT Security · Finance",
    deadline: null,
    resolution:
      "Finance Policy must explicitly state IT Security assessment is a prerequisite for all software spend, regardless of value threshold.",
    citations: [
      {
        document: "Finance_Expense_Policy.md",
        section: "§3.1",
        passage:
          "Department managers have authority to approve software subscriptions and SaaS purchases under $5,000 per year without secondary approvals.",
        confidence: 0.77,
        topic: "software procurement and security approval",
      },
      {
        document: "IT_Security_Policy.md",
        section: "§11.4",
        passage:
          "All software, including cloud and SaaS applications, must undergo formal IT Security risk assessment and obtain written sign-off prior to procurement, regardless of cost.",
        confidence: 0.76,
        topic: "software procurement and security approval",
      },
    ],
  },
  {
    id: "7",
    has_conflict: true,
    title: "Data minimization vs. indefinite retention",
    severity: "MEDIUM",
    confidence: 74,
    sources: ["Data_Governance_Policy.md §3", "Employee_Handbook.md §20"],
    affected: "HR · Legal · All employees",
    deadline: null,
    resolution:
      "Define a retention schedule with specific periods by data category. Handbook §20 must align with Data Governance minimization principles.",
    citations: [
      {
        document: "Data_Governance_Policy.md",
        section: "§3",
        passage:
          "In alignment with data minimization principles, employee personal records and performance evaluations must be destroyed 12 months post-employment.",
        confidence: 0.74,
        topic: "data minimization and retention",
      },
      {
        document: "Employee_Handbook.md",
        section: "§20",
        passage:
          "Nexora retains all historical employee training logs, performance reviews, and compliance records indefinitely to support career tracing and alumni validation.",
        confidence: 0.72,
        topic: "data minimization and retention",
      },
    ],
  },
  {
    id: "8",
    has_conflict: true,
    title: "Mandatory MFA vs. contractor exception authority",
    severity: "MEDIUM",
    confidence: 71,
    sources: ["IT_Security_Policy.md §7", "HR_Remote_Work_Policy.md §4"],
    affected: "IT Security · HR · Contractor workforce",
    deadline: null,
    resolution:
      "Remove manager exception authority from HR Remote Work §4. MFA must be mandatory without exception.",
    citations: [
      {
        document: "IT_Security_Policy.md",
        section: "§7",
        passage:
          "Multi-Factor Authentication (MFA) is mandatory for all access to company networks and systems, with no exceptions for any user type.",
        confidence: 0.71,
        topic: "MFA and authentication exceptions",
      },
      {
        document: "HR_Remote_Work_Policy.md",
        section: "§4",
        passage:
          "External contractors and temporary staff may be granted network access without MFA if approved in writing by their sponsoring department manager.",
        confidence: 0.70,
        topic: "MFA and authentication exceptions",
      },
    ],
  },
  {
    id: "9",
    has_conflict: true,
    title: "Emergency expenses: receipt vs. self-certification",
    severity: "MEDIUM",
    confidence: 68,
    sources: ["Finance_Expense_Policy.md §8", "Employee_Handbook.md §22"],
    affected: "Finance · All employees",
    deadline: null,
    resolution:
      "Minor. Align definition of 'emergency expense' across both policies. Handbook §22 threshold should match Finance Policy process.",
    citations: [
      {
        document: "Finance_Expense_Policy.md",
        section: "§8",
        passage:
          "No expense reimbursement will be processed without a valid receipt or invoice from the merchant. Self-certification of expenses is strictly prohibited.",
        confidence: 0.68,
        topic: "expense reimbursement validation",
      },
      {
        document: "Employee_Handbook.md",
        section: "§22",
        passage:
          "For emergency travel or critical supply procurement under $100, employees may self-certify the expense using the emergency form if a receipt was unobtainable.",
        confidence: 0.67,
        topic: "expense reimbursement validation",
      },
    ],
  },
];

// Timing config — controls the animation rhythm of the demo.
// Each step reveals after STEP_INTERVAL_MS * stepIndex + STEP_OFFSET_MS.
export const STEP_INTERVAL_MS = 950;
export const STEP_OFFSET_MS = 500;

// Conflict reveal schedule: which trace step index triggers which conflicts.
// At step index 1 (ConflictDetector, data residency): reveal conflict 0
// At step index 5 (ConflictDetector, anonymity): reveal conflicts 1 & 2
// At step index 6 (ResolutionRecommender, done): reveal all remaining
export const CONFLICT_REVEAL_MAP = {
  1: [0],         // conflict index 0 = Data Residency
  5: [1, 2],      // conflict indexes 1,2 = Anonymity + Incident Reporting
  6: [3, 4, 5, 6, 7, 8], // reveal remaining 6 conflicts
};
