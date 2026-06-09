"""
agents/orchestrator.py

ConflictSenseOrchestrator — coordinates the reasoning pipeline.

Spec reference: docs/system_architecture.md §3, docs/reliability_spec.md §1-3
                docs/agent_contracts.md

Responsibilities:
  - Run DocumentAnalyzer → ConflictDetector in sequence for each supported topic
  - Emit SSE events via a callback as each stage completes
  - Validate every ConflictDetector result: must have >= 2 distinct citations
  - Fall back to Tier 3 mock mode on any unhandled exception
  - Set _meta.fallback = "MOCK_MODE" when Tier 3 activates

Agents NOT included here (Phase 3):
  - ImpactAssessor
  - RiskQuantifier
  - ResolutionRecommender

Confidence thresholds (docs/reliability_spec.md §2):
  HIGH   (85-100%): shown on dashboard
  MEDIUM (65-84%):  shown with REVIEW REQUIRED badge
  LOW    (0-64%):   routed to human review queue only

SSE events emitted (in order per topic):
  evidence_retrieved         — DocumentAnalyzer completed for this topic
  conflict_candidate_detected — ConflictDetector raw output (before validation)
  conflict_validated         — citation/confidence validation passed
  conflict_emitted           — ConflictRecord ready (also triggers conflict_detected)
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from agents.document_analyzer import DocumentAnalyzer, DocumentAnalyzerResult, SUPPORTED_TOPICS
from agents.conflict_detector import ConflictDetector
from agents.conflict_validator import ConflictValidatorAgent
from agents.impact_assessor import ImpactAssessor
from agents.risk_quantifier import RiskQuantifier
from agents.resolution_recommender import ResolutionRecommender
from agents.conflict_types import ConflictRecord, ConflictStatus

logger = logging.getLogger("conflictsense.orchestrator")

# Confidence thresholds (docs/reliability_spec.md §2) — stored as 0-100 int
HIGH_THRESHOLD:   int = 85
MEDIUM_THRESHOLD: int = 65

# Type alias for the SSE emit callback
EmitFn = Callable[[str, dict], Any]


# ─── Result Types ──────────────────────────────────────────────────────────────

@dataclass
class OrchestratorResult:
    """Summary of a complete orchestrator run."""
    conflicts: list[ConflictRecord]
    uncertain_count: int
    blocked_count: int
    is_mock_mode: bool
    execution_time_s: float
    topics_analyzed: list[str] = field(default_factory=list)


# ─── ConflictSenseOrchestrator ────────────────────────────────────────────────

class ConflictSenseOrchestrator:
    """
    Coordinates DocumentAnalyzer → ConflictDetector for all supported topics.

    Usage:
        async def emit(event, data): yield sse_event(event, data)
        orchestrator = ConflictSenseOrchestrator()
        result = await orchestrator.run_analysis(emit)

    The emit_fn is called synchronously within the async run_analysis method.
    It is expected to be a thin wrapper around the SSE generator's yield.
    """

    def __init__(
        self,
        analyzer: Optional[DocumentAnalyzer] = None,
        detector: Optional[ConflictDetector] = None,
        validator_agent: Optional[ConflictValidatorAgent] = None,
        impact_assessor: Optional[ImpactAssessor] = None,
        risk_quantifier: Optional[RiskQuantifier] = None,
        resolution_recommender: Optional[ResolutionRecommender] = None,
    ) -> None:
        self._analyzer = analyzer or DocumentAnalyzer()
        self._detector = detector or ConflictDetector()
        self._validator_agent = validator_agent or ConflictValidatorAgent()
        self._impact_assessor = impact_assessor or ImpactAssessor()
        self._risk_quantifier = risk_quantifier or RiskQuantifier()
        self._resolution_recommender = resolution_recommender or ResolutionRecommender()

    async def run_analysis(self, emit_fn: EmitFn) -> OrchestratorResult:
        """
        Run the full DocumentAnalyzer → ConflictDetector pipeline.

        For each topic in SUPPORTED_TOPICS:
          1. Run DocumentAnalyzer — emit evidence_retrieved
          2. Run ConflictDetector — emit conflict_candidate_detected
          3. Validate result      — emit conflict_validated or blocked
          4. If valid             — emit conflict_emitted + conflict_detected

        Args:
            emit_fn: Callable(event_name, data_dict) called for each SSE event.

        Returns:
            OrchestratorResult with all confirmed conflicts.
        """
        t0 = time.monotonic()
        all_conflicts:  list[ConflictRecord] = []
        uncertain_count = 0
        blocked_count   = 0
        is_mock_mode    = False

        try:
            for topic in SUPPORTED_TOPICS:
                logger.info("Orchestrator: analyzing topic %r", topic)

                # ── DocumentAnalyzer ──────────────────────────────────────────
                analyzer_result = self._run_analyzer(topic)
                if analyzer_result.is_mock_mode:
                    is_mock_mode = True

                emit_fn("evidence_retrieved", self._build_evidence_event(analyzer_result))
                logger.info(
                    "Orchestrator: evidence_retrieved — %d citations for %r",
                    len(analyzer_result.citations), topic,
                )

                # Emit as trace_step for frontend (DocumentAnalyzer step)
                emit_fn("trace_step", self._build_da_trace_step(analyzer_result))

                # ── ConflictDetector ──────────────────────────────────────────
                detector_result = self._detector.detect(analyzer_result)
                if detector_result.is_mock_mode:
                    is_mock_mode = True

                uncertain_count += len(detector_result.uncertain_findings)
                blocked_count   += len(detector_result.blocked_findings)

                if not detector_result.conflicts and not detector_result.uncertain_findings:
                    # Emit a no-conflict trace step so the UI trace stays alive
                    emit_fn("trace_step", {
                        "agent": "ConflictDetector",
                        "agentColor": "#F09595",
                        "time": f"{detector_result.execution_time_s:.1f}s",
                        "query": None,
                        "citations": None,
                        "conclusion": f"No structural conflict found for topic: {topic}.",
                        "severity": None,
                        "confidence": None,
                    })
                    continue

                # Emit conflict_candidate_detected (before validation)
                for record in detector_result.conflicts + detector_result.uncertain_findings:
                    emit_fn("conflict_candidate_detected", {
                        "topic": topic,
                        "raw_confidence": record.confidence,
                        "severity": record.severity.value,
                        "sources": record.sources,
                    })
                    logger.info(
                        "Orchestrator: conflict_candidate_detected — %s (conf=%d%%)",
                        record.title, record.confidence,
                    )

                # Process confirmed conflicts
                for record in detector_result.conflicts:
                    # Validate (docs/reliability_spec.md §3)
                    is_valid, reason = self._validate_conflict(record)
                    emit_fn("conflict_validated", {
                        "id": record.id,
                        "passed": is_valid,
                        "reason": reason,
                    })

                    if not is_valid:
                        blocked_count += 1
                        logger.warning("Orchestrator: conflict blocked — %s: %s", record.id, reason)
                        continue

                    # Run ConflictValidatorAgent
                    record = self._validator_agent.validate(record)
                    if record.status == ConflictStatus.REJECTED:
                        emit_fn("conflict_rejected", {
                            "id": record.id,
                            "topic": topic,
                            "reason": record.reasoning
                        })
                        # Emit ConflictValidator trace step
                        emit_fn("trace_step", {
                            "agent": "ConflictValidator",
                            "agentColor": "#D085EB",
                            "time": "live",
                            "query": None,
                            "citations": None,
                            "conclusion": record.reasoning,
                            "severity": None,
                            "confidence": None,
                        })
                        continue
                    
                    # Emit ConflictValidator trace step for valid case
                    emit_fn("trace_step", {
                        "agent": "ConflictValidator",
                        "agentColor": "#D085EB",
                        "time": "live",
                        "query": None,
                        "citations": None,
                        "conclusion": "Validation passed: structural impossibility confirmed.",
                        "severity": None,
                        "confidence": None,
                    })

                    # Run ImpactAssessor
                    record = self._impact_assessor.assess(record, topic)
                    
                    # Emit ImpactAssessor trace step
                    emit_fn("trace_step", {
                        "agent": "ImpactAssessor",
                        "agentColor": "#EBD085",
                        "time": "live",
                        "query": None,
                        "citations": None,
                        "conclusion": record.affected,
                        "severity": None,
                        "confidence": None,
                    })

                    # Run RiskQuantifier
                    emit_fn("risk_assessment_started", {
                        "id": record.id,
                        "topic": topic,
                        "conflict": record.title,
                    })
                    risk_assessment = self._risk_quantifier.quantify(record, topic)

                    for category in risk_assessment.risk_categories:
                        emit_fn("risk_category_identified", {
                            "id": record.id,
                            "category": category,
                            "risk_level": risk_assessment.risk_level.value,
                        })

                    emit_fn("risk_validated", {
                        "id": record.id,
                        "risk_level": risk_assessment.risk_level.value,
                        "risk_score": risk_assessment.risk_score,
                        "confidence": risk_assessment.confidence,
                    })
                    emit_fn("trace_step", self._build_risk_trace_step(risk_assessment))
                    emit_fn("risk_assessment_complete", {
                        "id": record.id,
                        "assessment": risk_assessment.to_dict(),
                    })

                    # Run ResolutionRecommender
                    record.resolution = self._resolution_recommender.recommend(record)

                    emit_fn("trace_step", {
                        "agent": "ResolutionRecommender",
                        "agentColor": "#5AB0F0",
                        "time": "live",
                        "query": None,
                        "citations": None,
                        "conclusion": record.resolution,
                        "severity": None,
                        "confidence": None,
                    })

                    # Build serializable dict for SSE
                    record_dict = self._conflict_to_dict(record)

                    emit_fn("conflict_emitted",  record_dict)
                    emit_fn("conflict_detected", record_dict)  # ← frontend compat alias

                    # Emit ConflictDetector trace step
                    emit_fn("trace_step", self._build_cd_trace_step(record))

                    all_conflicts.append(record)
                    logger.info(
                        "Orchestrator: conflict_emitted — %r (%s, %d%%)",
                        record.title, record.severity.value, record.confidence,
                    )

        except Exception as exc:
            logger.error("Orchestrator: pipeline failed (%s) — mock fallback required.", exc)
            raise

        elapsed = time.monotonic() - t0
        logger.info(
            "Orchestrator complete in %.2fs — %d conflicts, %d uncertain, %d blocked, mock=%s",
            elapsed, len(all_conflicts), uncertain_count, blocked_count, is_mock_mode,
        )

        return OrchestratorResult(
            conflicts=all_conflicts,
            uncertain_count=uncertain_count,
            blocked_count=blocked_count,
            is_mock_mode=is_mock_mode,
            execution_time_s=elapsed,
            topics_analyzed=list(SUPPORTED_TOPICS),
        )

    # ── Private Helpers ────────────────────────────────────────────────────────

    def _run_analyzer(self, topic: str) -> DocumentAnalyzerResult:
        """Run DocumentAnalyzer with error isolation."""
        try:
            return self._analyzer.analyze(topic)
        except Exception as exc:
            logger.error("Orchestrator: DocumentAnalyzer failed for %r: %s", topic, exc)
            raise

    @staticmethod
    def _validate_conflict(record: ConflictRecord) -> tuple[bool, str]:
        """
        Validate a ConflictRecord meets the minimum bar for emission.
        Rule: must have >= 2 distinct source documents (reliability_spec §3).
        """
        distinct_docs = {c.document for c in record.citations}
        if len(distinct_docs) < 2:
            return False, f"Only {len(distinct_docs)} distinct source document(s) — minimum 2 required"
        if record.confidence < MEDIUM_THRESHOLD:
            return False, f"Confidence {record.confidence}% below UNCERTAIN threshold {MEDIUM_THRESHOLD}%"
        return True, "ok"

    # ── SSE Payload Builders ───────────────────────────────────────────────────

    @staticmethod
    def _build_evidence_event(result: DocumentAnalyzerResult) -> dict:
        return {
            "topic": result.topic,
            "citation_count": len(result.citations),
            "documents_queried": len(result.citations) + len(result.silent_documents),
            "silent_documents": result.silent_documents,
            "is_mock_mode": result.is_mock_mode,
        }

    @staticmethod
    def _build_da_trace_step(result: DocumentAnalyzerResult) -> dict:
        """
        Builds the trace_step payload for the DocumentAnalyzer.
        Extracts telemetry and diagnostic metadata directly from the result.
        """
        return {
            "agent": "DocumentAnalyzer",
            "agentColor": "#85B7EB",
            "time": f"{result.execution_time_s:.1f}s",
            "query": result.topic,
            "citations": [
                {
                    "document":   c.document,
                    "section":    c.section,
                    "passage":    c.passage,
                    "confidence": c.confidence,
                    "topic":      c.topic,
                }
                for c in result.citations
            ],
            "conclusion": None,
            "severity":   None,
            "confidence": None,
            "telemetry": {
                "docs_analyzed": len(result.per_doc_results),
                "total_citations": len(result.citations),
                "per_document_meta": result.per_doc_results
            }
        }

    @staticmethod
    def _build_cd_trace_step(record: ConflictRecord) -> dict:
        """Build the ConflictDetector trace step for the Reasoning Trace UI."""
        return {
            "agent":      "ConflictDetector",
            "agentColor": "#F09595",
            "time":       "live",
            "query":      None,
            "citations":  None,
            "conclusion": record.reasoning,
            "severity":   record.severity.value,
            "confidence": record.confidence,
            "isSurprise": record.isSurprise or False,
        }

    @staticmethod
    def _build_risk_trace_step(risk_assessment) -> dict:
        """Build the RiskQuantifier trace step for the Reasoning Trace UI."""
        return {
            "agent": "RiskQuantifier",
            "agentColor": "#F0B05A",
            "time": f"{risk_assessment.execution_time_s:.1f}s",
            "query": None,
            "citations": risk_assessment.supporting_evidence,
            "conclusion": risk_assessment.reasoning,
            "severity": risk_assessment.risk_level.value,
            "confidence": risk_assessment.confidence,
        }

    @staticmethod
    def _conflict_to_dict(record: ConflictRecord) -> dict:
        """Serialise a ConflictRecord to a JSON-safe dict matching ConflictRecord schema."""
        d: dict = {
            "id":           record.id,
            "has_conflict": record.has_conflict,
            "title":        record.title,
            "severity":     record.severity.value,
            "confidence":   record.confidence,
            "sources":      record.sources,
            "affected":     record.affected,
            "deadline":     record.deadline,
            "resolution":   record.resolution,
            "citations": [
                {
                    "document":   c.document,
                    "section":    c.section,
                    "passage":    c.passage,
                    "confidence": c.confidence,
                    "topic":      c.topic,
                }
                for c in record.citations
            ],
        }
        if record.isSurprise:
            d["isSurprise"] = True
        if record.risk_assessment is not None:
            d["risk_assessment"] = record.risk_assessment.to_dict()
        return d

    # ── Phase 3 Placeholders ───────────────────────────────────────────────────
    # These will be replaced by ResolutionRecommender.

    @staticmethod
    def _placeholder_resolution(record: ConflictRecord) -> str:
        return (
            f"Resolution pending ResolutionRecommender — "
            f"review {record.severity.value} conflict across {len(record.sources)} sources."
        )
