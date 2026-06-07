# IT Security Policy — Nexora Technologies
# Department: IT Infrastructure
# Effective: January 2024 | Last Reviewed: January 2024
# Classification: INTERNAL — MANDATORY COMPLIANCE

---

## §1. Purpose and Scope

This policy governs all information security controls for Nexora Technologies systems, infrastructure, and data. It applies to all employees, contractors, consultants, and third-party vendors who access Nexora systems in any capacity.

Non-compliance constitutes a disciplinary offence and may result in immediate termination and regulatory referral.

---

## §2. Acceptable Use

§2.1 — All company devices and systems must be used exclusively for business purposes. Personal use is prohibited on production systems.

§2.2 — Employees must not share credentials, access tokens, or private keys under any circumstances.

§2.3 — Unapproved software installation on company-managed devices is strictly prohibited.

---

## §3. Network Access

§3.1 — All remote access to Nexora internal systems must be conducted exclusively via the company-issued VPN client.

§3.2 — VPN access is restricted to connections originating from IP ranges pre-approved by IT Infrastructure. Access from unapproved geographic regions is automatically blocked.

---

## §4. Data Residency and Processing

§4.1 — Nexora operates a US-primary infrastructure model. All core data processing pipelines are hosted on US-domiciled servers in the US East Azure region.

§4.2 — All company data processing shall occur exclusively on US-domiciled servers. VPN access restricted to US IP ranges. Routing employee data through non-US infrastructure without explicit CTO authorisation constitutes a policy breach.

§4.3 — Cross-border data transfer is prohibited without written approval from the Chief Data Officer and General Counsel.

---

## §5. Device Management

§5.1 — Company-issued devices are subject to full-disk encryption (AES-256), remote-wipe capability, and Mobile Device Management (MDM) enrollment.

§5.2 — Lost or stolen devices must be reported to IT Security within one hour of discovery.

---

## §6. BYOD (Bring Your Own Device)

§6.1 — Personal devices may be used for email and calendar access only, provided the device is enrolled in MDM.

§6.2 — Sensitive data categories (financial records, HR data, client PII) must never be stored on personal devices.

§6.3 — Upon termination or transfer, all company data stored on personal devices (BYOD) must be immediately and permanently deleted. The employee must provide written confirmation of deletion to IT Security within 48 hours.

---

## §7. Authentication

§7.1 — Multi-Factor Authentication (MFA) is mandatory for all access to company networks and systems, with no exceptions for any user type.

§7.2 — MFA tokens must be hardware-based (FIDO2/YubiKey) for all privileged access accounts.

§7.3 — Passwords must be a minimum of 16 characters, renewed every 90 days, and must not repeat the last 10 passwords.

---

## §8. Data Classification

§8.1 — All data must be classified as: Public, Internal, Confidential, or Restricted.

§8.2 — Restricted data requires encryption at rest and in transit, with access limited to named individuals via role-based access control (RBAC).

---

## §9. Incident Reporting

§9.1 — Security incidents must be reported internally to the CISO within 72 hours to comply with FCA regulatory reporting mandates. No external whistleblowing reports are processed by security. All security incidents bypass standard HR and ethics channels.

§9.2 — The CISO is required to notify the FCA within 72 hours of a confirmed material breach. Failure to meet this deadline constitutes a separate regulatory infraction.

§9.3 — Employees who identify a potential security incident must not investigate independently. The incident must be reported to security@nexora.com immediately.

---

## §10. Third-Party Access

§10.1 — Third-party access to Nexora systems requires a signed Data Processing Agreement (DPA) and a completed Vendor Security Assessment.

§10.2 — Third-party access is time-limited and must be revoked upon contract expiry.

---

## §11. Software Procurement

§11.1 — All hardware and software procurement requests must be submitted through the IT Asset Management system.

§11.2 — No software license may be purchased without IT Security review, regardless of budget threshold.

§11.3 — Open-source software used in production environments requires a license review and a security scan before deployment.

§11.4 — All software, including cloud and SaaS applications, must undergo formal IT Security risk assessment and obtain written sign-off prior to procurement, regardless of cost.

---

## §12. Logging and Monitoring

§12.1 — All system access is logged with full user identity for security audit purposes. No exceptions permitted. Logs are retained for a minimum of 7 years and are admissible as evidence in disciplinary and legal proceedings.

§12.2 — Log integrity is maintained through cryptographic hash chaining. Logs may not be modified, deleted, or exported without CISO authorisation.

§12.3 — IT Security conducts automated anomaly detection on all access logs. Anomalies trigger escalation to the CISO within 15 minutes.

---

## §13. Enforcement

Violations of this policy are subject to immediate suspension, termination, and possible referral to regulatory authorities including the FCA. No grace periods apply.

*Policy Owner: CISO, IT Infrastructure*
*Review Cycle: Annual*
