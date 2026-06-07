"""
backend/models.py
Pydantic schemas enforcing data contracts exactly.

Spec reference: docs/data_contracts.md
"""

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel


# ─── §1: PolicyStatement ──────────────────────────────────────────────────────

class PolicyStatement(BaseModel):
    """A single grounded citation retrieved from one policy document."""
    document: str        # e.g. "IT_Security_Policy.md"
    section: str         # e.g. "§4.2"
    passage: str         # Exact text from the document
    confidence: float    # Foundry IQ retrieval confidence 0.0–1.0
    topic: str           # The query topic that produced this citation


class RiskAssessment(BaseModel):
    """Grounded enterprise risk assessment for a validated conflict."""
    risk_level: str
    risk_score: int
    risk_categories: List[str]
    reasoning: str
    supporting_evidence: List[PolicyStatement]
    confidence: int
    affected_entities: List[str]
    potential_consequences: List[str]
    uncertainty: Optional[str] = None
    execution_time_s: float = 0.0


# ─── §2: ConflictRecord ───────────────────────────────────────────────────────

class ConflictRecord(BaseModel):
    """A detected structural impossibility between two or more policy statements."""
    id: str
    has_conflict: bool
    title: str
    severity: str                           # "CRITICAL" | "HIGH" | "MEDIUM"
    confidence: int                         # 0–100 integer percentage
    sources: List[str]                      # e.g. ["IT_Security_Policy.md §4.2", ...]
    affected: str                           # Affected population / systems prose
    deadline: Optional[str] = None          # e.g. "July 1, 2026 — 24 days"
    resolution: str                         # Recommended resolution prose
    isSurprise: Optional[bool] = None       # True if unexpected finding
    citations: List[PolicyStatement] = []   # Underlying Foundry IQ evidence
    risk_assessment: Optional[RiskAssessment] = None


# ─── §3: TraceStep ───────────────────────────────────────────────────────────

class TraceStep(BaseModel):
    """One step in the Reasoning Trace UI feed."""
    agent: str                                    # "DocumentAnalyzer", etc.
    agentColor: str                               # Hex color for UI
    time: str                                     # Execution time e.g. "0.8s"
    query: Optional[str] = None                   # Query sent to Foundry IQ, if any
    citations: Optional[List[PolicyStatement]] = None
    conclusion: Optional[str] = None              # Prose reasoning paragraph (NEVER JSON)
    severity: Optional[str] = None
    confidence: Optional[int] = None
    isSurprise: Optional[bool] = None


# ─── Request / Response bodies ────────────────────────────────────────────────

class ApproveRequest(BaseModel):
    """Body for POST /approve — human approves a conflict finding."""
    conflict_id: str


class RejectRequest(BaseModel):
    """Body for POST /reject — human marks finding as false positive."""
    conflict_id: str


class ActionResponse(BaseModel):
    """Generic response for approve / reject actions."""
    status: str   # "approved" | "rejected"
    conflict_id: str
