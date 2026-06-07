"""
agents/conflict_helpers.py

Shared utilities for conflict detection, moved out of conflict_detector.py
for codebase governance and separation of concerns.
"""

from typing import Optional

from agents.conflict_types import (
    ConflictSeverity,
    ConflictStatus,
    ConflictType,
    ConflictRecord,
)
from agents.document_analyzer import PolicyStatement

# Confidence thresholds
HIGH_CONF_THRESHOLD: float = 0.85
MEDIUM_CONF_THRESHOLD: float = 0.65
MIN_CITATIONS: int = 2

class ValidationError(Exception):
    """Raised when a conflict finding fails citation or confidence validation."""

class InsufficientCitationsError(ValidationError):
    """Raised when fewer than MIN_CITATIONS distinct citations are present."""

class SchemaValidator:
    """Enforces reliability rules."""

    @staticmethod
    def validate_citations(citations: list[PolicyStatement]) -> None:
        distinct: set[tuple[str, str]] = set()
        for c in citations:
            if c.document and c.section and c.passage and c.passage.strip():
                distinct.add((c.document, c.section))
        if len(distinct) < MIN_CITATIONS:
            raise InsufficientCitationsError(
                f"Conflict requires ≥ {MIN_CITATIONS} distinct Foundry IQ citations; "
                f"only {len(distinct)} valid source(s) provided. Finding BLOCKED."
            )

    @staticmethod
    def validate_citation_completeness(citation: PolicyStatement) -> bool:
        return bool(
            citation.document
            and citation.section
            and citation.passage
            and citation.passage.strip()
            and 0.0 <= citation.confidence <= 1.0
        )

    @staticmethod
    def classify_confidence(confidence_float: float) -> tuple[ConflictStatus, int]:
        score = max(0, min(100, int(round(confidence_float * 100))))
        if confidence_float >= MEDIUM_CONF_THRESHOLD:
            return ConflictStatus.CONFIRMED, score
        return ConflictStatus.UNCERTAIN, score

    @staticmethod
    def validate_schema(record: ConflictRecord) -> list[str]:
        errors: list[str] = []
        if not record.id:
            errors.append("id is required")
        if not record.title or not record.title.strip():
            errors.append("title is required")
        if not record.reasoning or not record.reasoning.strip():
            errors.append("reasoning is required")
        if record.confidence < 0 or record.confidence > 100:
            errors.append(f"confidence {record.confidence} out of range 0–100")
        if not record.sources:
            errors.append("sources must not be empty")
        if not record.citations:
            errors.append("citations must not be empty")
        if record.has_conflict and not record.conflict_pairs:
            errors.append("conflict_pairs must not be empty when has_conflict is true")
        return errors

class DuplicateFilter:
    """Prevents the same conflict from being emitted twice."""

    def __init__(self) -> None:
        self._seen: set[frozenset[tuple[str, str]]] = set()

    def is_duplicate(self, citations: list[PolicyStatement]) -> bool:
        return frozenset((c.document, c.section) for c in citations) in self._seen

    def record(self, citations: list[PolicyStatement]) -> None:
        self._seen.add(frozenset((c.document, c.section) for c in citations))

    def reset(self) -> None:
        self._seen.clear()

class ConfidenceFramework:
    """Maps confidence floats to tiers and infers conflict types."""

    @staticmethod
    def get_tier_label(confidence_float: float) -> str:
        if confidence_float >= HIGH_CONF_THRESHOLD:
            return "HIGH"
        elif confidence_float >= MEDIUM_CONF_THRESHOLD:
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def severity_from_llm(llm_severity: Optional[str]) -> ConflictSeverity:
        if llm_severity:
            s = str(llm_severity).upper().strip()
            if s == "CRITICAL":
                return ConflictSeverity.CRITICAL
            if s == "HIGH":
                return ConflictSeverity.HIGH
            if s == "MEDIUM":
                return ConflictSeverity.MEDIUM
        return ConflictSeverity.MEDIUM

    @staticmethod
    def infer_conflict_type(why_impossible: str) -> ConflictType:
        text = why_impossible.lower()
        if any(w in text for w in ["server", "jurisdiction", "residency", "processing location"]):
            return ConflictType.DATA_RESIDENCY
        if any(w in text for w in ["retain", "retention", "delete", "deletion", "destroy"]):
            return ConflictType.RETENTION
        if any(w in text for w in ["approval", "authorization", "discretionary", "automatic"]):
            return ConflictType.APPROVAL_WORKFLOW
        if any(w in text for w in ["mfa", "multi-factor", "exception", "access"]):
            return ConflictType.ACCESS_CONTROL
        if any(w in text for w in ["department policy", "corporate policy", "hierarchy"]):
            return ConflictType.POLICY_HIERARCHY
        return ConflictType.DIRECT_CONTRADICTION
