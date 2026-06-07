"""
agents/conflict_types.py

Shared enumerations and data classes for the ConflictDetector pipeline.

Spec reference: docs/data_contracts.md §2, docs/reliability_spec.md §2
                docs/agent_contracts.md §2

This module contains ONLY data definitions — no logic, no I/O.
It exists so that conflict_detector.py, orchestrator.py, and
backend/pipeline.py can all import the same types without circular imports.

Single responsibility: data contracts for conflict detection outputs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from agents.document_analyzer import PolicyStatement


# ─── Severity / Status Enumerations ───────────────────────────────────────────

class ConflictSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH     = "HIGH"
    MEDIUM   = "MEDIUM"


class ConflictStatus(str, Enum):
    CONFIRMED = "CONFIRMED"   # confidence ≥ 0.65 — shown on dashboard
    UNCERTAIN = "UNCERTAIN"   # confidence < 0.65 — routed to human review queue only
    REJECTED  = "REJECTED"    # Failed semantic validation (e.g. semantic ambiguity)


class ConflictType(str, Enum):
    DIRECT_CONTRADICTION  = "Direct Contradiction"
    DATA_RESIDENCY        = "Data Residency Conflict"
    RETENTION             = "Retention Conflict"
    APPROVAL_WORKFLOW     = "Approval Workflow Conflict"
    ACCESS_CONTROL        = "Access Control Conflict"
    POLICY_HIERARCHY      = "Policy Hierarchy Violation"


# ─── Conflict Pair ─────────────────────────────────────────────────────────────

@dataclass
class ConflictPair:
    """A pair (or group) of statements identified as mutually impossible."""
    statement_a: PolicyStatement
    statement_b: PolicyStatement
    conflict_type: ConflictType
    why_impossible: str   # Plain English. Must be understandable by a judge.


# ─── ConflictRecord ───────────────────────────────────────────────────────────

@dataclass
class ConflictRecord:
    """
    Detected policy conflict — exactly matches docs/data_contracts.md §2.

    Validity invariants:
      - has_conflict is True
      - len(citations) >= 2
      - confidence >= 65 (CONFIRMED) or status == UNCERTAIN
    """
    id: str
    has_conflict: bool
    title: str
    severity: ConflictSeverity
    confidence: int                    # 0–100 integer (docs/data_contracts.md §2)
    sources: list[str]                 # ["IT_Security_Policy.md §4.2", ...]
    affected: str                      # Prose — filled by ImpactAssessor (Phase 3)
    deadline: Optional[str]            # e.g. "July 1, 2026 — 24 days" or None
    resolution: str                    # Prose — filled by ResolutionRecommender (Phase 3)
    citations: list[PolicyStatement]   # ≥ 2 Foundry IQ grounded citations
    conflict_pairs: list[ConflictPair] = field(default_factory=list)
    reasoning: str = ""                # Full prose explanation (shown in UI)
    status: ConflictStatus = ConflictStatus.CONFIRMED
    conflict_type: Optional[ConflictType] = None
    isSurprise: Optional[bool] = None
    is_mock_mode: bool = False
    risk_assessment: Optional[Any] = None


# ─── DetectorResult ───────────────────────────────────────────────────────────

@dataclass
class DetectorResult:
    """
    Full output of a single ConflictDetector.detect() call for one topic.
    Contains confirmed conflicts, uncertain findings, and blocked findings.
    """
    topic: str
    conflicts: list[ConflictRecord]        # CONFIRMED, ≥ 65% confidence
    uncertain_findings: list[ConflictRecord]  # < 65% — human review queue only
    blocked_findings: list[dict]           # Failed citation / schema validation
    is_mock_mode: bool
    execution_time_s: float
    tier_used: int                         # 1, 2, or 3
