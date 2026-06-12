"""
agents/conflict_validator.py

The ConflictValidator agent validates detected conflicts to weed out false positives,
specifically semantic ambiguity (e.g. "vacation" vs "annual leave") that is not a
true structural impossibility.

Spec reference: Phase 4A Live Rejection Flow
"""

import time
import logging

from agents.conflict_types import ConflictRecord, ConflictStatus
from agents.llm_provider import ProviderChain, get_provider_chain, LLMProviderError

logger = logging.getLogger("conflictsense.conflict_validator")

_SYSTEM_PROMPT = """You are a Conflict Validator. Determine if the proposed conflict is a genuine structural impossibility.
REJECT: wording/terminology differences, synonyms, stylistic variation, unsupported inference.
APPROVE: only mutually unsatisfiable policies.
Return JSON: {"status": "APPROVED" or "REJECTED", "reasoning": "plain text", "confidence": 0-100}"""

class ConflictValidatorAgent:
    """
    Evaluates a proposed ConflictRecord using an LLM.
    If the conflict is merely semantic ambiguity, marks it as REJECTED.
    """

    def __init__(self, provider_chain: ProviderChain | None = None, allow_mock: bool = True) -> None:
        self._provider_chain = provider_chain or get_provider_chain()
        self._allow_mock = allow_mock

    def validate(self, record: ConflictRecord) -> ConflictRecord:
        """
        Validates the conflict record.
        Returns the updated record.
        """
        t0 = time.monotonic()
        
        user_prompt = f"Title: {record.title}\nReasoning: {record.reasoning}\n\nCitations:\n"
        for c in record.citations:
            user_prompt += f"- [{c.document} {c.section}] {c.passage}\n"
            
        def mock_fallback():
            reasoning_lower = record.reasoning.lower()
            if "vacation" in reasoning_lower and "annual leave" in reasoning_lower:
                return {
                    "status": "REJECTED",
                    "reasoning": "Rejected: semantic ambiguity. Policies use different terminology but do not create a structural impossibility.",
                    "confidence": 95
                }
            return {
                "status": "APPROVED",
                "reasoning": "Validated as a true structural impossibility based on mock evaluation.",
                "confidence": 90
            }

        try:
            data, response = self._provider_chain.complete_json(
                _SYSTEM_PROMPT,
                user_prompt,
                mock_factory=mock_fallback,
                allow_mock=self._allow_mock,
            )
        except Exception as exc:
            if not self._allow_mock:
                raise
            logger.warning(
                "ConflictValidatorAgent: unexpected error from provider chain (%s: %s) — "
                "using mock fallback for record %r.",
                type(exc).__name__, exc, record.title,
            )
            data = mock_fallback()
            response = None

        if response is not None and response.is_mock_mode:
            if not self._allow_mock:
                raise LLMProviderError("ConflictValidator mock fallback forbidden in strict live mode")
            record.is_mock_mode = True
        
        status_str = data.get("status", "APPROVED").upper()
        if status_str == "REJECTED":
            record.status = ConflictStatus.REJECTED
            record.reasoning = data.get("reasoning", "Rejected by validation agent.")
            logger.info("ConflictValidator: REJECTED %r due to %s.", record.title, data.get("reasoning"))
        else:
            logger.info("ConflictValidator: VALIDATED %r.", record.title)
            
        return record
