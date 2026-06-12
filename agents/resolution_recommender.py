"""
agents/resolution_recommender.py

ResolutionRecommender generates concrete, owner-assigned resolution steps.
It uses the shared non-Azure LLM provider chain and deterministic Tier 3
fallback so remediation advice never breaks the SSE workflow.
"""

from __future__ import annotations

import logging
import time

from agents.conflict_types import ConflictRecord
from agents.llm_provider import ProviderChain, get_provider_chain, LLMProviderError

logger = logging.getLogger("conflictsense.resolution_recommender")

_SYSTEM_PROMPT = (
    "You are a policy resolution architect. Propose a concrete resolution to the given conflict. "
    "Assign ownership to specific departments and include a deadline if a regulatory timeline is present.\n"
    "CRITICAL: Do NOT use markdown code blocks or `json fences. Return JSON only: {\"recommendation\": \"1-2 sentence action\", \"owners\": [\"departments\"], \"deadline\": \"deadline or Immediate\"}\n"
    "No markdown code blocks."
)


class ResolutionRecommender:
    def __init__(self, provider_chain: ProviderChain | None = None, azure_client=None, allow_mock: bool = True) -> None:
        if azure_client is not None:
            logger.warning("ResolutionRecommender ignores Azure clients; using non-Azure provider chain.")
        self._provider_chain = provider_chain or get_provider_chain()
        self._allow_mock = allow_mock

    def recommend(self, record: ConflictRecord) -> str:
        t0 = time.monotonic()
        user_prompt = f"Conflict: {record.title}\nReasoning: {record.reasoning}\n"
        for citation in record.citations:
            user_prompt += f"\nDocument: {citation.document}\nPassage: {citation.passage}\n"

        fallback = (
            f"Policy owner and Compliance should reconcile this {record.severity.value} conflict "
            f"across {len(record.sources)} cited sources, publish the controlling rule, and route "
            "the change through human approval before remediation."
        )
        response = self._provider_chain.complete_text(
            _SYSTEM_PROMPT,
            user_prompt,
            mock_factory=lambda: fallback,
            allow_mock=self._allow_mock,
        )
        if not self._allow_mock and response.is_mock_mode:
            raise LLMProviderError("ResolutionRecommender mock fallback forbidden in strict live mode")
        elapsed = time.monotonic() - t0
        logger.info(
            "ResolutionRecommender: recommended %r via %s in %.2fs",
            record.title,
            response.provider,
            elapsed,
        )
        return response.content.strip() or fallback
