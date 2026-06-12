"""
tests/test_pipeline_stabilization.py

Targeted regression tests for the ConflictSense pipeline stabilization fixes.

Covers the issues identified in the Phase 1 root-cause analysis:

  Fix A: ProviderChain default order is Groq → Nvidia (OpenRouter removed — 402).
  Fix B: _parse_json is idempotent and handles edge cases correctly.
  Fix C: ConflictValidatorAgent survives unexpected transport exceptions.
  Fix D: vacation_policy mock correctly returns has_conflict=False.
  Fix E: _parse_json logs when brace-extraction fallback is used.
"""

from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

import pytest

from agents.llm_provider import (
    ProviderChain,
    GeminiProvider,
    GroqProvider,
    NvidiaProvider,
    LLMResponse,
    LLMProviderError,
    _parse_json,
    get_provider_chain,
    reset_provider_chain,
)
from agents.conflict_validator import ConflictValidatorAgent
from agents.conflict_types import ConflictRecord, ConflictSeverity, ConflictStatus
from agents.document_analyzer import PolicyStatement
from agents.iq_mock_data import get_conflict_mock_response


# ─── Fix A: ProviderChain default order ───────────────────────────────────────

class TestProviderChainDefaultOrder:
    """Verify Groq-first chain with OpenRouter removed (returns 402)."""

    def test_default_chain_excludes_gemini(self):
        chain = ProviderChain()
        names = [p.name for p in chain.providers]
        assert "gemini" not in names, "Gemini must remain disabled until rate limits are resolved"

    def test_default_chain_excludes_openrouter(self):
        chain = ProviderChain()
        names = [p.name for p in chain.providers]
        assert "openrouter" not in names, "OpenRouter must be removed — returns 402 Payment Required"

    def test_default_chain_includes_groq(self):
        chain = ProviderChain()
        names = [p.name for p in chain.providers]
        assert "groq" in names, "Default chain must include GroqProvider"

    def test_default_chain_includes_nvidia(self):
        chain = ProviderChain()
        names = [p.name for p in chain.providers]
        assert "nvidia" in names, "Default chain must include NvidiaProvider"

    def test_groq_before_nvidia(self):
        chain = ProviderChain()
        names = [p.name for p in chain.providers]
        assert names.index("groq") < names.index("nvidia"), (
            "Groq must appear before NVIDIA in the default chain"
        )

    def test_exact_order_is_groq_nvidia(self):
        chain = ProviderChain()
        names = [p.name for p in chain.providers]
        assert names == ["groq", "nvidia"], (
            f"Expected [groq, nvidia], got {names}"
        )

    def test_reset_provider_chain_clears_singleton(self):
        """reset_provider_chain() must invalidate the singleton."""
        import agents.llm_provider as mod
        original = mod._default_chain
        get_provider_chain()  # ensures singleton is created
        reset_provider_chain()
        assert mod._default_chain is None
        get_provider_chain()  # recreates it
        assert mod._default_chain is not None


# ─── Fix B: _parse_json edge cases ────────────────────────────────────────────

class TestParseJsonRobustness:
    """_parse_json must handle common LLM output quirks without crashing."""

    def test_valid_object(self):
        result = _parse_json('{"has_conflict": false}')
        assert result == {"has_conflict": False}

    def test_object_with_preamble(self):
        """LLMs often emit a sentence before the JSON object."""
        result = _parse_json('Here is the result:\n{"has_conflict": false}')
        assert result["has_conflict"] is False

    def test_object_with_trailing_text(self):
        result = _parse_json('{"has_conflict": false}\nHope that helps!')
        assert result["has_conflict"] is False

    def test_markdown_fenced_json(self):
        """Fenced code blocks are recovered via brace-extraction."""
        fenced = '```json\n{"has_conflict": true, "confidence": 0.9}\n```'
        result = _parse_json(fenced)
        assert result["has_conflict"] is True

    def test_top_level_list_coerced(self):
        """A list with a single dict element should be coerced to that dict."""
        result = _parse_json('[{"has_conflict": false}]')
        assert result == {"has_conflict": False}

    def test_garbage_raises(self):
        with pytest.raises(Exception):
            _parse_json("This is not JSON at all.")

    def test_nested_list_raises(self):
        """A list of lists cannot be coerced and must raise."""
        with pytest.raises((ValueError, Exception)):
            _parse_json('[["a", "b"]]')

    def test_empty_string_raises(self):
        with pytest.raises(Exception):
            _parse_json("")

    def test_parse_json_extraction_fallback_logs_debug(self, caplog):
        """When brace-extraction fires, a DEBUG message must be emitted."""
        with caplog.at_level(logging.DEBUG, logger="conflictsense.llm_provider"):
            _parse_json('prefix text {"key": "value"} suffix text')
        # Either a debug or warning log should mention the extraction
        relevant_records = [
            r for r in caplog.records
            if "extract" in r.message.lower() or "parse" in r.message.lower()
        ]
        assert len(relevant_records) >= 1, (
            "brace-extraction must emit at least one log record"
        )

    def test_no_json_object_warns(self, caplog):
        """When no JSON object is found at all, a WARNING must be emitted."""
        with caplog.at_level(logging.WARNING, logger="conflictsense.llm_provider"):
            with pytest.raises(Exception):
                _parse_json("no braces here")
        warnings = [r for r in caplog.records if r.levelno >= logging.WARNING]
        assert len(warnings) >= 1, "Missing JSON object must emit a WARNING log"


# ─── Fix C: ConflictValidatorAgent transport-exception guard ──────────────────

class TestConflictValidatorExceptionGuard:
    """ConflictValidatorAgent must not propagate unexpected transport exceptions."""

    def _make_record(self) -> ConflictRecord:
        stmt = PolicyStatement(
            document="A.md", section="§1",
            passage="All data must be protected.",
            confidence=0.9, topic="test",
        )
        return ConflictRecord(
            id="x1", has_conflict=True, title="Test conflict",
            severity=ConflictSeverity.CRITICAL, confidence=90,
            sources=["A.md §1"], affected="all employees", deadline=None,
            resolution="", citations=[stmt],
            reasoning="Data residency conflict.",
        )

    def test_ssl_error_does_not_propagate(self):
        """An ssl.SSLError inside the provider must be caught by the validator."""
        import ssl

        mock_chain = MagicMock(spec=ProviderChain)
        mock_chain.complete_json.side_effect = ssl.SSLError("handshake failed")

        validator = ConflictValidatorAgent(provider_chain=mock_chain)
        record = self._make_record()

        # Must not raise; should return record with APPROVED or REJECTED status
        result = validator.validate(record)
        assert result is not None
        assert result.status in (ConflictStatus.CONFIRMED, ConflictStatus.REJECTED)

    def test_connection_error_does_not_propagate(self):
        """A connection error must be caught and mock fallback used."""
        import httpx

        mock_chain = MagicMock(spec=ProviderChain)
        mock_chain.complete_json.side_effect = httpx.ConnectError("connection refused")

        validator = ConflictValidatorAgent(provider_chain=mock_chain)
        record = self._make_record()

        result = validator.validate(record)
        assert result is not None

    def test_runtime_error_does_not_propagate(self):
        mock_chain = MagicMock(spec=ProviderChain)
        mock_chain.complete_json.side_effect = RuntimeError("unexpected internal error")

        validator = ConflictValidatorAgent(provider_chain=mock_chain)
        record = self._make_record()

        result = validator.validate(record)
        assert result is not None

    def test_exception_is_logged(self, caplog):
        """The transport exception must be logged as a WARNING (not swallowed silently)."""
        mock_chain = MagicMock(spec=ProviderChain)
        mock_chain.complete_json.side_effect = RuntimeError("probe error")

        validator = ConflictValidatorAgent(provider_chain=mock_chain)
        record = self._make_record()

        with caplog.at_level(logging.WARNING, logger="conflictsense.conflict_validator"):
            validator.validate(record)

        warnings = [r for r in caplog.records if r.levelno >= logging.WARNING]
        assert len(warnings) >= 1, "Transport exception must be logged as WARNING"
        assert "probe error" in warnings[0].message or "RuntimeError" in warnings[0].message


# ─── Fix D: vacation_policy mock correctness ──────────────────────────────────

class TestVacationPolicyMockCorrectness:
    """The vacation_policy Tier 3 mock must return has_conflict=False."""

    def test_vacation_policy_mock_has_no_conflict(self):
        response = get_conflict_mock_response("vacation and leave terminology")
        assert response["has_conflict"] is False, (
            "vacation policy is a synonym difference — must NOT be flagged as a conflict"
        )

    def test_vacation_policy_mock_empty_conflict_pairs(self):
        response = get_conflict_mock_response("vacation and leave terminology")
        assert response["conflict_pairs"] == [], (
            "No conflict_pairs should be emitted for a synonym difference"
        )

    def test_vacation_policy_mock_zero_confidence(self):
        response = get_conflict_mock_response("vacation and leave terminology")
        assert response["confidence"] == 0.0, (
            "Confidence must be 0.0 for a non-conflict"
        )

    def test_vacation_policy_mock_null_severity(self):
        response = get_conflict_mock_response("vacation and leave terminology")
        assert response["severity"] is None, (
            "Severity must be None for a non-conflict"
        )

    def test_vacation_policy_detector_emits_no_conflict(self):
        """When Tier 3 fires for vacation policy, the detector must emit zero confirmed conflicts."""
        from agents.conflict_detector import ConflictDetector
        from agents.document_analyzer import DocumentAnalyzerResult

        stmt_a = PolicyStatement(
            document="Employee_Handbook.md", section="§5.1",
            passage="All employees are entitled to 20 vacation days per calendar year.",
            confidence=0.80, topic="vacation and leave terminology",
        )
        stmt_b = PolicyStatement(
            document="HR_Remote_Work_Policy.md", section="§7.2",
            passage="Annual leave entitlement is 20 working days per year for all staff.",
            confidence=0.78, topic="vacation and leave terminology",
        )

        with patch("agents.conflict_detector.AZURE_ENDPOINT", ""), \
             patch("agents.conflict_detector.AZURE_API_KEY", ""):
            detector = ConflictDetector()

        result_input = DocumentAnalyzerResult(
            topic="vacation and leave terminology",
            query="What rule or policy applies to: vacation and leave terminology?",
            citations=[stmt_a, stmt_b],
            low_confidence_citations=[],
            silent_documents=[],
            is_mock_mode=True,
            execution_time_s=0.0,
        )
        dr = detector.detect(result_input)

        assert len(dr.conflicts) == 0, (
            "Tier 3 mock for vacation policy must produce ZERO confirmed conflicts"
        )
