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
import os

from agents.conflict_types import ConflictRecord
from agents.iq_mock_data import topic_key_for, IMPACT_MOCKS

logger = logging.getLogger("conflictsense.impact_assessor")

_SYSTEM_PROMPT = """You are an enterprise impact analyst. Based ONLY on the Foundry IQ entity extractions provided, quantify the affected systems, teams, and employee populations for the following policy conflict. Do not hallucinate numbers. If numbers are not in the text, state the affected departments broadly."""

class ImpactAssessor:
    """
    Analyzes business impact of a conflict.
    Implements Tier 1 Azure call with Tier 3 Mock Mode fallback.
    """

    def __init__(self, azure_client=None) -> None:
        self._azure_client = azure_client
        self._available = False
        
        if self._azure_client is not None:
            self._available = True
        else:
            try:
                from openai import AzureOpenAI
                if os.getenv("AZURE_OPENAI_ENDPOINT") and os.getenv("AZURE_OPENAI_API_KEY"):
                    self._azure_client = AzureOpenAI(
                        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
                        api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
                        api_version=os.getenv("AZURE_API_VERSION", "2025-01-01-preview"),
                    )
                    self._available = True
            except ImportError:
                pass

    def assess(self, record: ConflictRecord, topic: str) -> ConflictRecord:
        """
        Populate the 'affected' field of the ConflictRecord.
        """
        t0 = time.monotonic()
        
        if self._available and self._azure_client:
            user_prompt = f"Topic: {topic}\nConflict: {record.title}\nReasoning: {record.reasoning}\n"
            for c in record.citations:
                user_prompt += f"\nDocument: {c.document}\nPassage: {c.passage}\n"
            
            try:
                deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_4O", "gpt-4o")
                response = self._azure_client.chat.completions.create(
                    model=deployment,
                    messages=[
                        {"role": "system", "content": _SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.0,
                    max_tokens=250,
                    timeout=10
                )
                impact = response.choices[0].message.content.strip()
                record.affected = impact
                elapsed = time.monotonic() - t0
                logger.info("ImpactAssessor: assessed %r live in %.2fs", record.title, elapsed)
                return record
            except Exception as e:
                logger.warning("ImpactAssessor: Azure LLM failed: %s", e)
        
        # In a full implementation, we'd call Azure OpenAI (Tier 1/2) using FoundryIQClient.
        # Here we rely on Tier 3 Mock Fallback.
        
        tkey = topic_key_for(topic)
        impact = IMPACT_MOCKS.get(tkey, "Affects unknown number of employees.")
        
        record.affected = impact
        
        elapsed = time.monotonic() - t0
        logger.info("ImpactAssessor: assessed %r mock in %.2fs", record.title, elapsed)
        
        return record
