# ConflictSense Synthetic Enterprise Specification

## Research Inputs Used
- research/00_frozen_decisions.md
- research/Pasted text(47).txt
- research/ConflictSense_UI.jsx

## Frozen Decisions Applied
- Enterprise = Nexora Technologies
- 7 specific policies required.

## Assumptions
- None.

---

## 1. Enterprise Profile
**Company:** Nexora Technologies
**Industry:** Financial Services / Tech
**Core Problem:** Highly regulated, globally distributed, with siloed policy creation leading to structural impossibilities.

## 2. Document Corpus (`knowledge_base/`)
The system depends on exactly 7 synthetic policy documents. They must be written with distinct departmental voices to reflect realistic enterprise silos.

1. **IT_Security_Policy.md**
   - *Voice:* 2019 Audit document. Strict, technical, unyielding.
   - *Key Rule:* "All system access is logged with full user identity for security audit purposes. No exceptions permitted."

2. **HR_Remote_Work_Policy.md**
   - *Voice:* COVID-era remote work accommodation. Permissive.

3. **Data_Governance_Policy.md**
   - *Voice:* Broad, principles-based legal document.

4. **Employee_Handbook.md**
   - *Voice:* Friendly, generic HR onboarding document.

5. **Whistleblower_Policy.md**
   - *Voice:* Serious, ethics-focused.
   - *Key Rule:* "Reports filed through the ethics portal are anonymous. Employee identity is never logged or traceable by any internal party."

6. **Finance_Expense_Policy.md**
   - *Voice:* Bureaucratic, cost-control focused.

7. **DPDP_Compliance_Directive.md** (New)
   - *Voice:* External law firm drafted in 2026. Regulatory panic.
   - *Key Rule:* DPDP Act compliance deadlines and strict data residency rules.

## 3. Pre-Seeded Conflicts
The documents are designed to guarantee specific, high-value conflicts that the agents will reliably detect:
- **Conflict 1:** Three-way data residency impossibility (IT mandates US servers, DPDP mandates Indian servers, HR permits global remote work for the same employees).
- **Conflict 2:** Anonymity guarantee is technically impossible (Whistleblower vs. IT Security logging).
- **Conflict 3:** Incident reporting gap (FCA vs. internal IT).
