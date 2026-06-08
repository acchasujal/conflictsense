"""
agents/resolution_recommender.py
ResolutionRecommender agent — generates concrete, owner-assigned resolution steps.

Spec reference: docs/agent_contracts.md §5, docs/foundry_iq_spec.md §2.3,
                docs/prompt_registry.md §5
"""

import logging
import time
import os
from agents.conflict_types import ConflictRecord

logger = logging.getLogger("conflictsense.resolution_recommender")

_SYSTEM_PROMPT = """You are a policy resolution architect. Propose a concrete resolution to the given conflict. Assign ownership to specific departments based on the policies involved, and establish a deadline if a regulatory timeline is present in the context. Output ONLY a plain text paragraph."""

class ResolutionRecommender:
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

    def recommend(self, record: ConflictRecord) -> str:
        t0 = time.monotonic()
        
        if self._available and self._azure_client:
            user_prompt = f"Conflict: {record.title}\nReasoning: {record.reasoning}\n"
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
                    temperature=0.2,
                    max_tokens=500,
                    timeout=10
                )
                resolution = response.choices[0].message.content.strip()
                elapsed = time.monotonic() - t0
                logger.info("ResolutionRecommender: recommended %r in %.2fs", record.title, elapsed)
                return resolution
            except Exception as e:
                logger.warning("ResolutionRecommender: Azure LLM failed: %s", e)
        
        # Fallback
        return f"Resolution pending — review {record.severity.value} conflict across {len(record.sources)} sources."
