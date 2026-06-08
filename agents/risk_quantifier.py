"""
RiskQuantifier agent - turns validated conflicts and impact into grounded risk.

This module does not classify rejected conflicts and does not invent penalties,
employee counts, or financial exposure. It uses only the ConflictRecord,
ImpactAssessor output, and grounded citations already present in the pipeline.
"""

from __future__ import annotations

import logging
import re
import time
import os
import json
from dataclasses import dataclass, field
from enum import Enum

from agents.conflict_types import ConflictRecord, ConflictSeverity, ConflictStatus

logger = logging.getLogger("conflictsense.risk_quantifier")

_SYSTEM_PROMPT = """You are a regulatory risk analyst. Based on the provided regulatory excerpts and the policy conflict, estimate the Regulatory, Operational, Legal, and Reputational risks. Provide your reasoning in plain text. Reference specific laws (e.g., DPDP Act) only if provided in the context.

You MUST return a JSON object with this exact structure:
{
  "risk_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "risk_score": integer (1-100),
  "risk_categories": ["list", "of", "strings"],
  "reasoning": "plain text reasoning",
  "potential_consequences": ["list", "of", "strings"],
  "uncertainty": "string or null"
}"""

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class RiskAssessment:
    risk_level: RiskLevel
    risk_score: int
    risk_categories: list[str]
    reasoning: str
    supporting_evidence: list[dict]
    confidence: int
    affected_entities: list[str]
    potential_consequences: list[str]
    uncertainty: str | None = None
    execution_time_s: float = 0.0

    def to_dict(self) -> dict:
        return {
            "risk_level": self.risk_level.value,
            "risk_score": self.risk_score,
            "risk_categories": self.risk_categories,
            "reasoning": self.reasoning,
            "supporting_evidence": self.supporting_evidence,
            "confidence": self.confidence,
            "affected_entities": self.affected_entities,
            "potential_consequences": self.potential_consequences,
            "uncertainty": self.uncertainty,
            "execution_time_s": round(self.execution_time_s, 2),
        }


class RiskQuantifier:
    """Grounded enterprise risk analyst for validated conflict records."""

    def __init__(self, azure_client=None):
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

    def quantify(self, record: ConflictRecord, topic: str | None = None) -> RiskAssessment:
        if record.status == ConflictStatus.REJECTED:
            raise ValueError("RiskQuantifier cannot process rejected conflicts.")
        if not record.has_conflict:
            raise ValueError("RiskQuantifier requires a validated conflict.")
        if len({c.document for c in record.citations}) < 2:
            raise ValueError("RiskQuantifier requires at least two grounded source documents.")

        t0 = time.monotonic()
        
        if self._available and self._azure_client:
            user_prompt = f"Topic: {topic}\nConflict: {record.title}\nReasoning: {record.reasoning}\nImpact: {record.affected}\n"
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
                    max_tokens=500,
                    response_format={"type": "json_object"},
                    timeout=15
                )
                
                data = json.loads(response.choices[0].message.content)
                
                assessment = RiskAssessment(
                    risk_level=RiskLevel(data["risk_level"]),
                    risk_score=data["risk_score"],
                    risk_categories=data["risk_categories"],
                    reasoning=data["reasoning"],
                    supporting_evidence=self._supporting_evidence(record),
                    confidence=min(record.confidence, self._evidence_confidence(record)),
                    affected_entities=self._affected_entities(record.affected),
                    potential_consequences=data["potential_consequences"],
                    uncertainty=data.get("uncertainty"),
                    execution_time_s=time.monotonic() - t0,
                )
                record.risk_assessment = assessment
                logger.info("RiskQuantifier: assessed %r live as %s", record.title, assessment.risk_level.value)
                return assessment
            except Exception as e:
                logger.warning("RiskQuantifier: Azure LLM failed (%s), falling back to rule-based.", e)
        text = self._combined_text(record, topic)
        categories = self._categories(text)
        affected_entities = self._affected_entities(record.affected)
        consequences = self._consequences(record, categories, text)
        risk_score = self._risk_score(record, categories, consequences)
        risk_level = self._risk_level(risk_score)
        uncertainty = self._uncertainty(record, text)

        assessment = RiskAssessment(
            risk_level=risk_level,
            risk_score=risk_score,
            risk_categories=categories,
            reasoning=self._reasoning(record, categories, consequences, uncertainty),
            supporting_evidence=self._supporting_evidence(record),
            confidence=min(record.confidence, self._evidence_confidence(record)),
            affected_entities=affected_entities,
            potential_consequences=consequences,
            uncertainty=uncertainty,
            execution_time_s=time.monotonic() - t0,
        )
        record.risk_assessment = assessment
        logger.info(
            "RiskQuantifier: assessed %r as %s (%d)",
            record.title,
            assessment.risk_level.value,
            assessment.risk_score,
        )
        return assessment

    @staticmethod
    def _combined_text(record: ConflictRecord, topic: str | None) -> str:
        citation_text = " ".join(c.passage for c in record.citations)
        return " ".join([
            topic or "",
            record.title,
            record.reasoning,
            record.affected,
            citation_text,
        ]).lower()

    @staticmethod
    def _categories(text: str) -> list[str]:
        rules = [
            ("Compliance Risk", ["dpdp", "gdpr", "regulatory", "compliance", "audit"]),
            ("Operational Risk", ["workflow", "process", "cannot", "impossible", "operational"]),
            ("Legal Risk", ["legal", "commitment", "promise", "liability", "guarantee"]),
            ("Reputational Risk", ["trust", "whistleblower", "anonymous", "anonymity", "public"]),
            ("Security Risk", ["logging", "identity", "access", "mfa", "security", "credential"]),
            ("Governance Risk", ["policy", "ownership", "approval", "inconsistency", "exception"]),
        ]
        categories = [name for name, words in rules if any(word in text for word in words)]
        return categories or ["Governance Risk"]

    @staticmethod
    def _affected_entities(impact: str) -> list[str]:
        cleaned = impact.strip()
        if not cleaned:
            return ["Affected entities are not specified in the grounded impact assessment."]
        parts = re.split(r";|\.", cleaned)
        return [part.strip() for part in parts if part.strip()] or [cleaned]

    @staticmethod
    def _consequences(record: ConflictRecord, categories: list[str], text: str) -> list[str]:
        consequences: list[str] = []
        if "anonymous" in text or "anonymity" in text:
            consequences.extend([
                "Employees may rely on an anonymity promise that cannot be fulfilled.",
                "Mandatory identity logging may compromise employee trust in reporting channels.",
                "Audit scrutiny is likely because policy commitments and system controls conflict.",
            ])
        if "Compliance Risk" in categories:
            consequences.append(
                "Compliance exposure may exist, but specific penalties are not quantified without grounded regulatory evidence."
            )
        if "Operational Risk" in categories:
            consequences.append("Teams may be unable to follow both policies at the same time.")
        if "Security Risk" in categories:
            consequences.append("Security controls may conflict with business or compliance commitments.")
        if not consequences:
            consequences.append(
                f"Leadership should review this {record.severity.value.lower()} conflict because it has validated evidence from multiple sources."
            )
        return list(dict.fromkeys(consequences))

    @staticmethod
    def _risk_score(
        record: ConflictRecord,
        categories: list[str],
        consequences: list[str],
    ) -> int:
        base = {
            ConflictSeverity.CRITICAL: 82,
            ConflictSeverity.HIGH: 68,
            ConflictSeverity.MEDIUM: 52,
        }[record.severity]
        category_bonus = min(len(categories) * 3, 12)
        consequence_bonus = min(len(consequences) * 2, 8)
        confidence_adjustment = max(min(record.confidence - 75, 8), -8)
        return max(1, min(100, base + category_bonus + consequence_bonus + confidence_adjustment))

    @staticmethod
    def _risk_level(score: int) -> RiskLevel:
        if score >= 85:
            return RiskLevel.CRITICAL
        if score >= 70:
            return RiskLevel.HIGH
        if score >= 45:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    @staticmethod
    def _uncertainty(record: ConflictRecord, text: str) -> str | None:
        if "penalty" in text or "%" in text or "$" in text:
            return (
                "Quantified penalties or financial exposure are not asserted unless they appear "
                "in grounded source evidence."
            )
        if not record.affected.strip() or "unknown" in record.affected.lower():
            return "The impacted population is not fully specified by grounded evidence."
        return None

    @staticmethod
    def _supporting_evidence(record: ConflictRecord) -> list[dict]:
        return [
            {
                "document": citation.document,
                "section": citation.section,
                "passage": citation.passage,
                "confidence": citation.confidence,
                "topic": citation.topic,
            }
            for citation in record.citations
        ]

    @staticmethod
    def _evidence_confidence(record: ConflictRecord) -> int:
        avg = sum(c.confidence for c in record.citations) / len(record.citations)
        return int(round(avg * 100))

    @staticmethod
    def _reasoning(
        record: ConflictRecord,
        categories: list[str],
        consequences: list[str],
        uncertainty: str | None,
    ) -> str:
        consequence_text = " ".join(consequences[:2])
        category_text = ", ".join(categories)
        uncertainty_text = f" {uncertainty}" if uncertainty else ""
        return (
            f"{record.title} creates {category_text}. {consequence_text} "
            f"The assessment is grounded in {len(record.citations)} cited policy passages "
            f"and the current impact assessment: {record.affected}.{uncertainty_text}"
        )
