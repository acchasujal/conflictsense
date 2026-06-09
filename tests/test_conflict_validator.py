"""
tests/test_conflict_validator.py

Tests for the ConflictValidatorAgent.
"""

from agents.conflict_validator import ConflictValidatorAgent
from agents.conflict_types import ConflictRecord, ConflictStatus
from agents.llm_provider import ProviderChain
import pytest

def test_validation_rejects_semantic_ambiguity(monkeypatch):
    # Create a mock provider chain that strictly uses the mock fallback
    class MockProviderChain(ProviderChain):
        def complete_json(self, system_prompt, user_prompt, *, mock_factory):
            # force mock fallback
            return mock_factory(), None
            
    validator = ConflictValidatorAgent(provider_chain=MockProviderChain())
    
    record = ConflictRecord(
        id="test-1",
        has_conflict=True,
        title="Vacation vs Annual Leave",
        severity="Medium",
        confidence=90,
        sources=[],
        affected="All employees",
        deadline=None,
        resolution="N/A",
        citations=[],
        reasoning="The employee handbook uses the term vacation, while the local policy uses annual leave."
    )
    
    updated_record = validator.validate(record)
    assert updated_record.status == ConflictStatus.REJECTED
    assert "semantic ambiguity" in updated_record.reasoning

def test_validation_approves_true_conflict(monkeypatch):
    class MockProviderChain(ProviderChain):
        def complete_json(self, system_prompt, user_prompt, *, mock_factory):
            return mock_factory(), None
            
    validator = ConflictValidatorAgent(provider_chain=MockProviderChain())
    
    record = ConflictRecord(
        id="test-2",
        has_conflict=True,
        title="Data Location Conflict",
        severity="High",
        confidence=90,
        sources=[],
        affected="All employees",
        deadline=None,
        resolution="N/A",
        citations=[],
        reasoning="IT Security requires US servers, but DPDP requires Indian servers. This is a mutually unsatisfiable policy constraint."
    )
    
    updated_record = validator.validate(record)
    assert updated_record.status == ConflictStatus.CONFIRMED
    assert updated_record.status != ConflictStatus.REJECTED
    # Actually the validator doesn't set status to VALIDATED, it just leaves it alone (PENDING) or changes it.
    # Let's check what the code does for APPROVED:
    # `status_str = data.get("status", "APPROVED").upper()`
    # `if status_str == "REJECTED": record.status = ConflictStatus.REJECTED`
    # `else: logger.info("ConflictValidator: VALIDATED...")`
    # So the status remains whatever it was (usually PENDING or OPEN). We will check that it's NOT REJECTED.
    assert updated_record.status != ConflictStatus.REJECTED
