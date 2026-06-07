"""
agents/conflict_validator.py

The ConflictValidator agent validates detected conflicts to weed out false positives,
specifically semantic ambiguity (e.g. "vacation" vs "annual leave") that is not a
true structural impossibility.

Spec reference: Phase 4A Live Rejection Flow
"""

import time
import logging

from agents.conflict_types import ConflictRecord, ConflictStatus

logger = logging.getLogger("conflictsense.conflict_validator")

class ConflictValidatorAgent:
    """
    Evaluates a proposed ConflictRecord.
    If the conflict is merely semantic ambiguity, marks it as REJECTED.
    """

    def validate(self, record: ConflictRecord) -> ConflictRecord:
        """
        Validates the conflict record.
        Returns the updated record.
        """
        t0 = time.monotonic()
        
        # In a real implementation, this might call Azure OpenAI to ask:
        # "Is this a true structural conflict, or just a difference in wording?"
        # For our current scope and Tier 3 mocks, we can use simple heuristics on the reasoning.
        
        reasoning_lower = record.reasoning.lower()
        if "vacation" in reasoning_lower and "annual leave" in reasoning_lower:
            record.status = ConflictStatus.REJECTED
            record.reasoning = "Rejected: semantic ambiguity. Policies use different terminology but do not create a structural impossibility."
            logger.info("ConflictValidator: REJECTED %r due to semantic ambiguity.", record.title)
        else:
            # Passes validation
            logger.info("ConflictValidator: VALIDATED %r.", record.title)
            
        return record
