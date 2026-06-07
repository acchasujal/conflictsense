# Innovation Summary

## Innovation in One Sentence
ConflictSense turns policy contradiction detection into an auditable reasoning workflow instead of a black-box answer generator.

## What Is New Here
- **Reasoning Trace as product:** The main artifact is not a chat response; it is a visible chain of reasoning.
- **Grounded multi-document comparison:** Foundry IQ is used per document to preserve citation fidelity and avoid context overload.
- **Structural impossibility detection:** The system looks for contradictions that cannot both be true, which is more valuable than simple similarity matching.
- **Human approval by design:** The workflow stops before action and requires explicit human intent.
- **Reliability as a feature:** The fallback chain is part of the product story, not a hidden implementation detail.

## Why It Feels Different
Most AI demos show how fast a model can answer a question.
ConflictSense shows how a model can support a defensible enterprise decision.

## Differentiation Summary
- Chatbots answer.
- Search tools retrieve.
- ConflictSense reasons, validates, and escalates.

## Submission Angle
The novelty judges should remember is not "we built an agent pipeline."
It is:
- a visible reasoning surface,
- grounded citations for every claim,
- human approval before action,
- and a domain-specific demonstration of compliance risk.
