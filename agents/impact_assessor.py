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

logger = logging.getLogger("conflictsense.impact_assessor")

class ImpactAssessor:
    """
    Analyzes business impact of a conflict.
    Currently implements Tier 3 Mock Mode fallback.
    """

    def __init__(self, azure_client=None) -> None:
        self._azure_client = azure_client
        self._available = False
        
        if azure_client is not None:
            self._available = True

    def assess(self, record: ConflictRecord, topic: str) -> ConflictRecord:
        """
        Populate the 'affected' field of the ConflictRecord.
        """
        t0 = time.monotonic()
        
        # In a full implementation, we'd call Azure OpenAI (Tier 1/2) using FoundryIQClient.
        # Here we rely on Tier 3 Mock Fallback.
        
        tkey = topic_key_for(topic)
        impact = IMPACT_MOCKS.get(tkey, "Affects unknown number of employees.")
        
        record.affected = impact
        
        elapsed = time.monotonic() - t0
        logger.info("ImpactAssessor: assessed %r in %.2fs", record.title, elapsed)
        
        return record
