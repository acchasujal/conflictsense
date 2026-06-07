from __future__ import annotations

import pytest

from agents.conflict_types import (
    ConflictRecord,
    ConflictSeverity,
    ConflictStatus,
    DetectorResult,
)
from agents.document_analyzer import DocumentAnalyzerResult, PolicyStatement
from agents.impact_assessor import ImpactAssessor
from agents.orchestrator import ConflictSenseOrchestrator
from agents.risk_quantifier import RiskLevel, RiskQuantifier


def _stmt(document: str, section: str, passage: str, confidence: float = 0.92) -> PolicyStatement:
    return PolicyStatement(
        document=document,
        section=section,
        passage=passage,
        confidence=confidence,
        topic="employee reporting channels and anonymity guarantees",
    )


def _anonymity_record() -> ConflictRecord:
    citations = [
        _stmt(
            "Whistleblower_Policy.md",
            "Sec. 4.2",
            "Reports filed through the ethics portal are anonymous. Employee identity is never logged.",
            0.91,
        ),
        _stmt(
            "IT_Security_Policy.md",
            "Sec. 12.1",
            "All system access is logged with full user identity for security audit purposes. No exceptions permitted.",
            0.95,
        ),
    ]
    return ConflictRecord(
        id="conflict-anonymity",
        has_conflict=True,
        title="Whistleblower Anonymity vs. IT Identity Logging",
        severity=ConflictSeverity.CRITICAL,
        confidence=91,
        sources=[f"{c.document} {c.section}" for c in citations],
        affected="Affects whistleblower reports submitted through the ethics portal.",
        deadline=None,
        resolution="",
        citations=citations,
        reasoning=(
            "The Whistleblower Policy promises anonymous reporting while the IT Security "
            "Policy requires identity logging for every access event."
        ),
        status=ConflictStatus.CONFIRMED,
        is_mock_mode=True,
    )


def test_risk_scoring_for_anonymity_conflict_is_highly_visible():
    assessment = RiskQuantifier().quantify(_anonymity_record())

    assert assessment.risk_level == RiskLevel.CRITICAL
    assert assessment.risk_score >= 85
    assert "Legal Risk" in assessment.risk_categories
    assert "Security Risk" in assessment.risk_categories
    assert "Governance Risk" in assessment.risk_categories
    assert "trust" in assessment.reasoning.lower()


def test_grounding_validation_requires_two_distinct_source_documents():
    record = _anonymity_record()
    record.citations = [record.citations[0]]

    with pytest.raises(ValueError, match="two grounded source documents"):
        RiskQuantifier().quantify(record)


def test_uncertainty_handling_does_not_assert_ungrounded_penalties():
    record = _anonymity_record()
    record.affected = "Affects unknown number of employees. Non-compliance penalty unknown."

    assessment = RiskQuantifier().quantify(record)

    assert assessment.uncertainty is not None
    assert "not asserted" in assessment.uncertainty
    assert "4%" not in assessment.reasoning


def test_rejected_conflicts_never_reach_risk_quantifier():
    record = _anonymity_record()
    record.status = ConflictStatus.REJECTED

    with pytest.raises(ValueError, match="rejected conflicts"):
        RiskQuantifier().quantify(record)


def test_impact_assessor_to_risk_quantifier_threads_affected_entities():
    record = ImpactAssessor().assess(
        _anonymity_record(),
        "employee reporting channels and anonymity guarantees",
    )
    assessment = RiskQuantifier().quantify(record)

    assert assessment.affected_entities
    assert any("whistleblower" in entity.lower() for entity in assessment.affected_entities)


class _FakeAnalyzer:
    def analyze(self, topic: str) -> DocumentAnalyzerResult:
        record = _anonymity_record()
        return DocumentAnalyzerResult(
            topic=topic,
            query=f"What rule or policy applies to: {topic}?",
            citations=record.citations,
            low_confidence_citations=[],
            silent_documents=[],
            is_mock_mode=True,
            execution_time_s=0.01,
        )


class _FakeDetector:
    def detect(self, analyzer_result: DocumentAnalyzerResult) -> DetectorResult:
        return DetectorResult(
            topic=analyzer_result.topic,
            conflicts=[_anonymity_record()],
            uncertain_findings=[],
            blocked_findings=[],
            is_mock_mode=True,
            execution_time_s=0.01,
            tier_used=3,
        )


@pytest.mark.anyio
async def test_orchestrator_emits_risk_sse_events_after_impact():
    events: list[tuple[str, dict]] = []
    orchestrator = ConflictSenseOrchestrator(
        analyzer=_FakeAnalyzer(),
        detector=_FakeDetector(),
        impact_assessor=ImpactAssessor(),
        risk_quantifier=RiskQuantifier(),
    )

    await orchestrator.run_analysis(lambda event, data: events.append((event, data)))

    event_names = [event for event, _ in events]
    assert "risk_assessment_started" in event_names
    assert "risk_category_identified" in event_names
    assert "risk_validated" in event_names
    assert "risk_assessment_complete" in event_names
    impact_index = next(
        idx for idx, (_, data) in enumerate(events)
        if data.get("agent") == "ImpactAssessor"
    )
    assert event_names.index("risk_assessment_started") > impact_index


@pytest.mark.anyio
async def test_end_to_end_pipeline_emits_conflict_impact_and_risk():
    events: list[tuple[str, dict]] = []
    orchestrator = ConflictSenseOrchestrator(
        analyzer=_FakeAnalyzer(),
        detector=_FakeDetector(),
        impact_assessor=ImpactAssessor(),
        risk_quantifier=RiskQuantifier(),
    )

    result = await orchestrator.run_analysis(lambda event, data: events.append((event, data)))

    assert result.conflicts
    assert result.conflicts[0].affected
    assert result.conflicts[0].risk_assessment is not None
    emitted = [data for event, data in events if event == "conflict_emitted"]
    assert emitted
    assert emitted[0]["risk_assessment"]["risk_level"] in {"HIGH", "CRITICAL"}
