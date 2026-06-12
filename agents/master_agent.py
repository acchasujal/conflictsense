"""
agents/master_agent.py

Master Reasoning Agent - executes full knowledge base analysis in a single LLM call.
This drastically reduces API calls and latency for the live and upload modes.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict

import asyncio

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
        self.provider_chain = get_provider_chain()
        self.allow_mock = allow_mock

    async def analyze(self, all_documents_text: str) -> Dict[str, Any]:
        """
        Runs the massive single-prompt analysis against the provided text.
        """
        prompt = MASTER_PROMPT.replace("{evidence}", all_documents_text)
        system_instruction = "You are an expert compliance auditor. You output ONLY valid JSON without markdown fences."
        
        logger.info("FAST_PIPELINE_START: MasterReasoningAgent executing single-call LLM analysis...")
        logger.info(f"CONTEXT_LENGTH: {len(all_documents_text)} characters loaded.")
        
        def _mock_factory():
            from pathlib import Path
            kb_path = Path(__file__).parent.parent / "data" / "precomputed" / "full_kb_analysis.json"
            if kb_path.exists():
                with open(kb_path, "r", encoding="utf-8") as f:
                    # Load the precomputed events and extract the first 'conflict_detected' or 'complete'
                    events = json.load(f)
                    conflicts = [ev["conflict_record"] for ev in events if "conflict_record" in ev]
                    exec_summary = "Enterprise Audit detected multiple high-risk compliance gaps across Finance, IT, and Legal. Immediate attention required."
                    return {"executive_summary": exec_summary, "conflicts": conflicts}
            return {"executive_summary": "Mock fallback used due to provider failure.", "conflicts": []}

        logger.info("LLM_CALL_START: Calling provider chain...")
        try:
            data, response = await asyncio.to_thread(
                self.provider_chain.complete_json,
                system_instruction,
                prompt,
                mock_factory=_mock_factory,
                allow_mock=self.allow_mock
            )
            
            logger.info("LLM_CALL_COMPLETE: Provider chain returned successfully.")
            logger.info(f"PROVIDER_SELECTED: {response.provider}")
            logger.info(f"MODEL_SELECTED: {response.model}")
            
            if response.is_mock_mode:
                logger.warning("MasterReasoningAgent fell back to mock data.")
                
            logger.info("JSON_PARSE_SUCCESS: Response parsed correctly.")
            conflicts = data.get("conflicts", [])
            logger.info(f"CONFLICTS_FOUND: {len(conflicts)}")
            
            return {"data": data, "is_mock": response.is_mock_mode}
        except Exception as e:
            logger.error(f"MasterReasoningAgent pipeline failure: {e}")
            return {"data": None, "is_mock": False}
