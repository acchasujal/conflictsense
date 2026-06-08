"""
agents/conflict_detector.py

ConflictDetector — the flagship reasoning engine of ConflictSense.

Spec reference:
    docs/agent_contracts.md   §2
    docs/prompt_registry.md   §2
    docs/reliability_spec.md  §2–3
    docs/data_contracts.md    §2

Responsibilities:
  - Receive DocumentAnalyzerResult (PolicyStatement list from ≥ 2 documents)
  - Identify pairs making logically / operationally impossible claims
  - Produce grounded PROSE reasoning — NOT JSON labels or bullet lists
  - Enforce: confidence < 0.65 → UNCERTAIN (never shown on dashboard)
  - Enforce: < 2 distinct citations → ValidationError (finding blocked)
  - Deduplicate: same citation set seen twice is suppressed

Data types (ConflictRecord, DetectorResult, etc.) live in agents/conflict_types.py.
Mock data for Tier 3 lives in agents/iq_mock_data.py.

Fallback chain (docs/reliability_spec.md §1):
  Tier 1: Azure gpt-4o     (10 s, temperature=0)
  Tier 2: Azure gpt-4o-mini (15 s, temperature=0)
  Tier 3: Pre-computed mock responses (never fails)
"""

from __future__ import annotations

import hashlib
import logging
import time
from typing import Optional

from dotenv import load_dotenv

from agents.document_analyzer import DocumentAnalyzerResult, PolicyStatement
from agents.llm_provider import ProviderChain, get_provider_chain
from agents.conflict_types import (
    ConflictSeverity,
    ConflictStatus,
    ConflictType,
    ConflictPair,
    ConflictRecord,
    DetectorResult,
)
from agents.iq_mock_data import get_conflict_mock_response, topic_key_for as _topic_key

load_dotenv()
logger = logging.getLogger("conflictsense.conflict_detector")

# ─── Configuration ─────────────────────────────────────────────────────────────

from agents.conflict_helpers import (
    SchemaValidator,
    DuplicateFilter,
    ConfidenceFramework,
    ValidationError,
    InsufficientCitationsError,
    MIN_CITATIONS,
)


# ─── System Prompt (verbatim from docs/prompt_registry.md §2) ─────────────────

_SYSTEM_PROMPT = """\
You are a policy conflict analyst. You receive N policy statements about the same topic, \
each from a different authoritative source document with a Foundry IQ citation. \
Your task: identify any pair or group of statements that make incompatible claims — \
claims that cannot simultaneously be satisfied for the same employee population. \
Explain, in plain language, WHY the conflict is logically impossible — not just that \
the statements differ. If a conflict requires a specific employee scenario to be impossible \
(e.g. Indian-resident remote workers), specify that scenario precisely. \
If no genuine conflict exists, say so. \
Return JSON: {has_conflict: boolean, conflict_pairs: [...], reasoning: string, \
severity: CRITICAL|HIGH|MEDIUM, confidence: float}

CRITICAL RULES:
1. Only report conflicts where it is STRUCTURALLY IMPOSSIBLE to satisfy both policies \
simultaneously for the same employee population. Wording differences, style differences, \
and complementary policies are NOT conflicts.
2. Every conflict_pair must reference the exact document names and section numbers provided.
3. The "reasoning" field must be a single prose paragraph written as a human compliance \
officer explaining the issue to a judge. Name both policies, state the exact logical \
impossibility, and explain the real-world consequence.
4. "confidence" must be a float 0.0–1.0.
5. If no genuine conflict: return {"has_conflict": false, "conflict_pairs": [], \
"reasoning": "No structural conflict found.", "severity": null, "confidence": 0.0}
6. Do NOT add any text outside the JSON object.
"""

_USER_PROMPT_TEMPLATE = """\
Topic: {topic}

Policy statements retrieved from enterprise documents:
{statements_block}

Identify any genuine structural conflict. Return ONLY the JSON object as specified.
"""


# ─── ConflictDetector ──────────────────────────────────────────────────────────

class ConflictDetector:
    """
    Policy conflict reasoning engine.

    Detects logical, operational, governance, and compliance impossibilities
    between PolicyStatement objects from different documents.

    Usage:
        result = DocumentAnalyzer().analyze(topic)
        detector = ConflictDetector()
        dr = detector.detect(result)
        for conflict in dr.conflicts:
            print(conflict.reasoning)
    """

    def __init__(self, provider_chain: Optional[ProviderChain] = None, azure_client=None) -> None:
        if azure_client is not None:
            logger.warning("ConflictDetector ignores Azure clients; using non-Azure provider chain.")
        self._provider_chain = provider_chain or get_provider_chain()
        self._validator = SchemaValidator()
        self._dup_filter = DuplicateFilter()
        self._confidence_fw = ConfidenceFramework()

    # ── Public Interface ───────────────────────────────────────────────────────

    def detect(self, analyzer_result: DocumentAnalyzerResult) -> DetectorResult:
        """
        Run conflict detection on a DocumentAnalyzerResult.

        Returns DetectorResult with confirmed conflicts, uncertain findings,
        and blocked findings.
        """
        t0 = time.monotonic()
        self._dup_filter.reset()

        topic     = analyzer_result.topic
        citations = analyzer_result.citations
        is_mock   = analyzer_result.is_mock_mode

        logger.info("ConflictDetector.detect() — topic: %r, citations: %d", topic, len(citations))

        if len(citations) < MIN_CITATIONS:
            logger.warning(
                "ConflictDetector: fewer than %d citations for %r — skipping.", MIN_CITATIONS, topic,
            )
            return DetectorResult(
                topic=topic, conflicts=[], uncertain_findings=[],
                blocked_findings=[{"reason": f"Fewer than {MIN_CITATIONS} citations", "topic": topic}],
                is_mock_mode=is_mock, execution_time_s=time.monotonic() - t0, tier_used=3,
            )

        raw, tier = self._call_with_fallback(topic, citations)
        if tier == 3:
            is_mock = True

        conflicts: list[ConflictRecord] = []
        uncertain: list[ConflictRecord] = []
        blocked:   list[dict] = []

        if raw.get("has_conflict", False):
            record = self._build_conflict_record(topic, raw, citations, is_mock)
            if record is None:
                blocked.append({"reason": "Citation/schema validation failed", "topic": topic})
            elif record.status == ConflictStatus.UNCERTAIN:
                uncertain.append(record)
                logger.info("ConflictDetector: UNCERTAIN (conf=%d%%) for %r.", record.confidence, topic)
            elif self._dup_filter.is_duplicate(record.citations):
                logger.info("ConflictDetector: duplicate suppressed for %r.", topic)
            else:
                self._dup_filter.record(record.citations)
                conflicts.append(record)
                logger.info(
                    "ConflictDetector: CONFIRMED — %r (%s, %d%%).",
                    record.title, record.severity.value, record.confidence,
                )
        else:
            logger.info("ConflictDetector: no conflict for %r.", topic)

        elapsed = time.monotonic() - t0
        logger.info(
            "ConflictDetector done in %.2fs — %d confirmed, %d uncertain, %d blocked (Tier %d).",
            elapsed, len(conflicts), len(uncertain), len(blocked), tier,
        )
        return DetectorResult(
            topic=topic, conflicts=conflicts, uncertain_findings=uncertain,
            blocked_findings=blocked, is_mock_mode=is_mock,
            execution_time_s=elapsed, tier_used=tier,
        )

    def detect_from_statements(
        self, topic: str, statements: list[PolicyStatement],
    ) -> DetectorResult:
        """Convenience: run detection directly from a list of PolicyStatements."""
        mock_result = DocumentAnalyzerResult(
            topic=topic,
            query=f"What rule or policy applies to: {topic}?",
            citations=statements,
            low_confidence_citations=[],
            silent_documents=[],
            is_mock_mode=False,
            execution_time_s=0.0,
        )
        return self.detect(mock_result)

    # ── LLM Call Chain ────────────────────────────────────────────────────────

    def _call_with_fallback(
        self, topic: str, citations: list[PolicyStatement],
    ) -> tuple[dict, int]:
        """Gemini -> OpenRouter -> Groq -> NVIDIA -> Tier 3 mock."""
        block = self._build_statements_block(citations)
        user_prompt = _USER_PROMPT_TEMPLATE.format(topic=topic, statements_block=block)
        try:
            data, response = self._provider_chain.complete_json(
                _SYSTEM_PROMPT,
                user_prompt,
                mock_factory=lambda: self._mock_response(topic),
            )
            if "has_conflict" not in data:
                raise ValueError("missing has_conflict")
            if data.get("has_conflict") and not data.get("conflict_pairs"):
                raise ValueError("conflict response missing conflict_pairs")
            return data, 3 if response.is_mock_mode else 1
        except Exception as exc:
            logger.warning("Provider chain produced unusable output for %r: %s", topic, exc)
            return self._mock_response(topic), 3

    def _mock_response(self, topic: str) -> dict:
        """Return a pre-computed mock response for the topic (Tier 3)."""
        return get_conflict_mock_response(topic)

    # ── Record Construction ───────────────────────────────────────────────────

    def _build_conflict_record(
        self, topic: str, raw: dict,
        citations: list[PolicyStatement], is_mock: bool,
    ) -> Optional[ConflictRecord]:
        """Build and validate a ConflictRecord from raw LLM output."""
        # Confidence
        try:
            conf_float = max(0.0, min(1.0, float(raw.get("confidence", 0.0))))
        except (TypeError, ValueError):
            conf_float = 0.0
        status, conf_int = self._validator.classify_confidence(conf_float)

        # Citation validation
        valid_cits = [c for c in citations if self._validator.validate_citation_completeness(c)]
        try:
            self._validator.validate_citations(valid_cits)
        except InsufficientCitationsError as exc:
            logger.warning("ConflictDetector: %s", exc)
            return None

        # Conflict pairs
        raw_pairs = raw.get("conflict_pairs", [])
        conflict_pairs = self._parse_conflict_pairs(raw_pairs, valid_cits)

        # Conflict type
        conflict_type: Optional[ConflictType] = None
        if conflict_pairs:
            conflict_type = conflict_pairs[0].conflict_type
        else:
            reasoning_text = raw.get("reasoning", "")
            if reasoning_text:
                conflict_type = self._confidence_fw.infer_conflict_type(reasoning_text)

        severity = self._confidence_fw.severity_from_llm(raw.get("severity"))
        reasoning = str(raw.get("reasoning", "")).strip()
        title = self._derive_title(topic, conflict_type, severity)
        sources = self._build_sources(valid_cits)

        # Deterministic ID from source fingerprint
        record_id = hashlib.sha1("|".join(sorted(sources)).encode()).hexdigest()[:8]

        record = ConflictRecord(
            id=record_id, has_conflict=True, title=title,
            severity=severity, confidence=conf_int,
            sources=sources, affected="", deadline=None, resolution="",
            citations=valid_cits, conflict_pairs=conflict_pairs,
            reasoning=reasoning, status=status,
            conflict_type=conflict_type, is_mock_mode=is_mock,
        )
        if raw.get("is_surprise"):
            record.isSurprise = True

        schema_errors = self._validator.validate_schema(record)
        if schema_errors:
            logger.warning("ConflictDetector: schema errors for %r: %s", topic, schema_errors)
            return None

        return record

    def _parse_conflict_pairs(
        self, raw_pairs: list[dict], citations: list[PolicyStatement],
    ) -> list[ConflictPair]:
        """Convert LLM conflict_pairs dicts to ConflictPair objects."""
        pairs: list[ConflictPair] = []
        cit_index = {(c.document, c.section): c for c in citations}

        if raw_pairs:
            for rp in raw_pairs:
                doc_a, sec_a = str(rp.get("document_a", "")), str(rp.get("section_a", ""))
                doc_b, sec_b = str(rp.get("document_b", "")), str(rp.get("section_b", ""))
                why = str(rp.get("why_impossible", "")).strip()

                stmt_a = cit_index.get((doc_a, sec_a)) or next(
                    (c for c in citations if c.document == doc_a), None)
                stmt_b = cit_index.get((doc_b, sec_b)) or next(
                    (c for c in citations if c.document == doc_b), None)

                if stmt_a and stmt_b:
                    ct = self._parse_conflict_type(str(rp.get("conflict_type", "")))
                    if ct is None and why:
                        ct = self._confidence_fw.infer_conflict_type(why)
                    pairs.append(ConflictPair(
                        statement_a=stmt_a, statement_b=stmt_b,
                        conflict_type=ct or ConflictType.DIRECT_CONTRADICTION,
                        why_impossible=why,
                    ))
        return pairs

    @staticmethod
    def _parse_conflict_type(raw: str) -> Optional[ConflictType]:
        mapping = {
            "Direct Contradiction":       ConflictType.DIRECT_CONTRADICTION,
            "Data Residency Conflict":    ConflictType.DATA_RESIDENCY,
            "Retention Conflict":         ConflictType.RETENTION,
            "Approval Workflow Conflict": ConflictType.APPROVAL_WORKFLOW,
            "Access Control Conflict":    ConflictType.ACCESS_CONTROL,
            "Policy Hierarchy Violation": ConflictType.POLICY_HIERARCHY,
        }
        return mapping.get(raw.strip())

    @staticmethod
    def _build_sources(citations: list[PolicyStatement]) -> list[str]:
        seen: set[str] = set()
        sources: list[str] = []
        for c in citations:
            src = f"{c.document} {c.section}".strip()
            if src not in seen:
                seen.add(src)
                sources.append(src)
        return sources

    @staticmethod
    def _derive_title(
        topic: str, conflict_type: Optional[ConflictType], severity: ConflictSeverity,
    ) -> str:
        if conflict_type == ConflictType.DATA_RESIDENCY:
            return "Data residency: structural impossibility"
        if conflict_type == ConflictType.RETENTION:
            return "Data retention: delete vs. retain impossibility"
        if conflict_type == ConflictType.APPROVAL_WORKFLOW:
            return "Approval workflow: entitlement vs. authorization gap"
        if conflict_type == ConflictType.ACCESS_CONTROL:
            return "Access control: MFA exception contradiction"
        if conflict_type == ConflictType.POLICY_HIERARCHY:
            return "Policy hierarchy: department overrides corporate mandate"
        return f"{severity.value}: conflict in {topic[:60]}"

    @staticmethod
    def _build_statements_block(citations: list[PolicyStatement]) -> str:
        lines: list[str] = []
        for i, c in enumerate(citations, start=1):
            lines.append(
                f"[{i}] {c.document} {c.section} (confidence={c.confidence:.2f}):\n"
                f'    "{c.passage}"\n'
            )
        return "\n".join(lines)


# ─── Convenience Functions ─────────────────────────────────────────────────────

_default_detector: Optional[ConflictDetector] = None


def get_detector() -> ConflictDetector:
    """Return the module-level singleton ConflictDetector."""
    global _default_detector
    if _default_detector is None:
        _default_detector = ConflictDetector()
    return _default_detector


def detect_conflicts(analyzer_result: DocumentAnalyzerResult) -> DetectorResult:
    """Top-level convenience function for the orchestrator."""
    return get_detector().detect(analyzer_result)
