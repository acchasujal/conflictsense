# Reliability Story

## Reliability Principle
The demo should never fail on stage, and the product should never present low-trust output as if it were certain.

## Reliability Design
- Primary path uses live Azure AI Search-backed analysis.
- Backup path preserves the same workflow with a lighter model tier.
- Mock fallback guarantees completion if live dependencies fail.

## Trust Controls
- Findings must have enough grounded Azure AI Search citations to be shown.
- Low-confidence outputs (<65%) are never promoted to the main dashboard.
- The Human Approval Gate stops autonomous action, ensuring an enterprise "Human-in-the-loop" before any business impact occurs.
- The UI surfaces a clear mock-mode indicator when fallback is active.

## Why Judges Should Notice
Reliability is part of the product value, not a backstage detail.
Enterprise buyers care whether a system:
- finishes,
- stays honest,
- and avoids presenting uncertain output as fact.

## What Makes This Strong
- It protects the demo from infrastructure risk.
- It protects the user from hallucinated certainty.
- It makes the system suitable for compliance-oriented workflows.

## Short Narrative
ConflictSense treats reliability as a first-class feature: if the live model path struggles, the user still gets a complete, transparent, and clearly labeled result.
