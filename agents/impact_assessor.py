"""
agents/impact_assessor.py

ImpactAssessor agent — affected population and systems quantifier.

Spec reference: docs/agent_contracts.md §3, docs/foundry_iq_spec.md §2.2,
                docs/prompt_registry.md §3

Responsibilities:
  - Query Foundry IQ for employee groups, systems, and teams mentioned in
    connection with the conflict topic
  - Return prose string for the ConflictRecord.affected field
  - In Tier 3 mock mode, retrieve hardcoded impact strings from iq_mock_data.py
"""

import logging
import time

from agents.conflict_types import ConflictRecord
from agents.iq_mock_data import topic_key_for, IMPACT_MOCKS
from agents.llm_provider import ProviderChain, get_provider_chain

logger = logging.getLogger("conflictsense.impact_assessor")

_SYSTEM_PROMPT = """You are an enterprise impact analyst. Based ONLY on the Foundry IQ entity extractions provided, quantify the affected systems, teams, and employee populations for the following policy conflict. Do not hallucinate numbers. If numbers are not in the text, state the affected departments broadly."""

class ImpactAssessor:
    """
    Analyzes business impact of a conflict.
    Implements Tier 1 Azure call with Tier 3 Mock Mode fallback.
    """

    def __init__(self, provider_chain: ProviderChain | None = None, azure_client=None) -> None:
        if azure_client is not None:
            logger.warning("ImpactAssessor ignores Azure clients; using non-Azure provider chain.")
        self._provider_chain = provider_chain or get_provider_chain()

    def assess(self, record: ConflictRecord, topic: str) -> ConflictRecord:
        """
        Populate the 'affected' field of the ConflictRecord.
        """
        t0 = time.monotonic()
        
        tkey = topic_key_for(topic)
        fallback = IMPACT_MOCKS.get(tkey, "Affects unknown number of employees.")
        user_prompt = f"Topic: {topic}\nConflict: {record.title}\nReasoning: {record.reasoning}\n"
        for c in record.citations:
            user_prompt += f"\nDocument: {c.document}\nPassage: {c.passage}\n"
        response = self._provider_chain.complete_text(
            _SYSTEM_PROMPT,
            user_prompt,
            mock_factory=lambda: fallback,
        )
        
        record.affected = response.content.strip() or fallback
        
        elapsed = time.monotonic() - t0
        logger.info("ImpactAssessor: assessed %r via %s in %.2fs", record.title, response.provider, elapsed)
        
        return record
