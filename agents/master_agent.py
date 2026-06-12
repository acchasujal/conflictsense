"""
agents/master_agent.py

Master Reasoning Agent - executes full knowledge base analysis in a single LLM call.
This drastically reduces API calls and latency for the live and upload modes.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict

from agents.llm_provider import get_provider_chain

logger = logging.getLogger("conflictsense.master_agent")

MASTER_PROMPT = """You are ConflictSense, an advanced Enterprise Policy Reasoning Agent.
Your task is to analyze the provided policy documents and identify ALL logical contradictions, compliance gaps, and structural impossibilities.

You MUST return a strictly formatted JSON object matching the following structure exactly. Do not include markdown fences or any other text.

{
  "executive_summary": "A brief 2-3 sentence summary of the overall policy health and the most critical findings.",
  "conflicts": [
    {
      "id": "A unique string ID for this conflict",
      "title": "A concise title",
      "severity": "CRITICAL, HIGH, or MEDIUM",
      "affected": "Description of the affected population or system",
      "confidence": 95,
      "sources": ["Policy_Name_1.md", "Policy_Name_2.md"],
      "citations": [
        {
          "document": "Policy_Name_1.md",
          "section": "Section X",
          "passage": "Exact quote from document",
          "confidence": 0.95
        }
      ],
      "risk_assessment": {
        "risk_level": "CRITICAL, HIGH, or MEDIUM",
        "risk_score": 90,
        "potential_consequences": ["Consequence 1"]
      },
      "resolution": "A detailed resolution recommendation.",
      "deadline": "Any compliance deadline mentioned, or null"
    }
  ]
}

EVIDENCE CONTEXT:
{evidence}
"""

class MasterReasoningAgent:
    def __init__(self, allow_mock: bool = False):
        self.provider_chain = get_provider_chain(allow_mock=allow_mock)

    async def analyze(self, all_documents_text: str) -> Dict[str, Any]:
        """
        Runs the massive single-prompt analysis against the provided text.
        """
        prompt = MASTER_PROMPT.format(evidence=all_documents_text)
        
        logger.info("MasterReasoningAgent executing single-call LLM analysis...")
        result = await self.provider_chain.generate(
            prompt=prompt,
            system_instruction="You are an expert compliance auditor. You output ONLY valid JSON without markdown fences."
        )
        
        if result.is_mock:
            logger.warning("MasterReasoningAgent fell back to mock data.")
            
        try:
            # Strip markdown fences if present
            raw_text = result.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            raw_text = raw_text.strip()
                
            data = json.loads(raw_text)
            return {"data": data, "is_mock": result.is_mock}
        except json.JSONDecodeError as e:
            logger.error(f"MasterReasoningAgent returned invalid JSON: {e}")
            logger.debug(f"Raw output: {result.text}")
            return {"data": None, "is_mock": result.is_mock}
