# ConflictSense README Specification

## Research Inputs Used
- research/Pasted text(47).txt
- research/00_frozen_decisions.md

## Frozen Decisions Applied
- Must embed SVG architecture diagram.
- Must explain the Foundry IQ ablation test results.

## Assumptions
- Standard GitHub README formatting.

---

## 1. Structure

### 1.1 Hero Section
- Title: ConflictSense
- Subtitle: Structural Impossibility Detection for Enterprise Policies.
- Must include the MVP hook: "Nexora's employees believe they can report harassment anonymously..."

### 1.2 The "Why Foundry IQ?" Section
- Must explicitly define why standard RAG fails (context overflow, hallucination, loss of section citations).
- Must explicitly state the ablation test result: "Replacing Foundry IQ with single-context concatenation produces (a) no section-level citations, (b) LLM paraphrases rather than exact language... (d) outputs that cannot be shown to a regulator."

### 1.3 Architecture Diagram
- Embed `docs/architecture.png` (or SVG) prominently.

### 1.4 How to Run Locally
- Instructions for `npm run dev` and FastAPI `uvicorn` startup.
- Mention `.env` setup for Azure API Keys.
- Explain how to trigger Tier 3 Mock Mode (set invalid API key).

### 1.5 Responsible AI
- Explain confidence routing.
- Explain the Human Approval Gate.
