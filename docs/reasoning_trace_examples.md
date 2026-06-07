# ConflictSense Reasoning Trace Examples

## Research Inputs Used
- research/Pasted text(47).txt
- research/ConflictSense_UI.jsx

## Frozen Decisions Applied
- The trace must show prose reasoning.

## Assumptions
- None.

---

## 1. DocumentAnalyzer Example
**Query:** "employee reporting channels and anonymity guarantees"
**Input:** Single document (Whistleblower_Policy.md)
**Citations Retrieved:**
- `Whistleblower_Policy.md §4.2` [High confidence]: "Reports filed through the ethics portal are anonymous. Employee identity is never logged or traceable by any internal party."
**Output:** (No explicit prose conclusion at this step, just passes citations to ConflictDetector).

## 2. ConflictDetector Example
**Input:** Citations from Whistleblower_Policy.md and IT_Security_Policy.md
**Output Prose (Golden Standard):**
"Nexora's Whistleblower Policy makes a legal commitment to every employee: your report cannot be traced. Its IT Security Policy makes a technical commitment: every system action is logged with user identity, no exceptions. These two statements cannot simultaneously be true. Every report filed through the ethics portal is traceable — full stop. The anonymity guarantee exists on paper. It does not exist in the system."

## 3. ImpactAssessor Example
**Input:** The anonymity conflict.
**Output Prose:**
"All 1,200 employees are theoretically affected. The affected systems include the primary ethics portal and the centralized IT logging server. The conflict requires resolution between the Legal & Compliance department (owners of the Whistleblower policy) and IT Security."

## 4. RiskQuantifier Example
**Input:** Regulatory context for Whistleblower laws and IT data logging.
**Output Prose:**
"Regulatory risk: HIGH. Failure to protect whistleblower anonymity violates standard protections. Operational risk: HIGH — employees face potential retaliation due to system logs. Legal exposure: HIGH. Reputational risk: CRITICAL."

## 5. ResolutionRecommender Example
**Input:** The anonymity conflict and RiskQuantifier outputs.
**Output Prose:**
"Migrate ethics portal to an off-system anonymous channel (e.g., third-party hotline) OR carve IT logging exceptions for ethics portal access. Requires Legal + IT Security Director alignment."
