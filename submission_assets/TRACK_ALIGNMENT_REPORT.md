# Track Alignment Report: Pivot to Reasoning Agents

This report details the systematic audit and removal of generic "Enterprise Track" language from the ConflictSense repository, ensuring strict alignment with the **Reasoning Agents** track evaluation criteria.

## Background

Early iterations of ConflictSense relied heavily on marketing buzzwords, positioning the tool as an "Enterprise Copilot" or a "Chatbot for Policies." This framing diluted the technical reality of the project. A Copilot implies an assistive, prompt-driven UI. ConflictSense is fundamentally a background, autonomous reasoning engine.

## Removals and Replacements

The following terminology pivots were executed across the README, UI documentation, and submission assets:

| Removed Terminology | Replaced With | Rationale |
| :--- | :--- | :--- |
| "Microsoft 365 Copilot positioning" | **Autonomous Policy Reasoning Engine** | Emphasizes the proactive, agentic nature of the system. |
| "Enterprise Agent" | **Reasoning Agent** | Aligns specifically with the hackathon track and highlights cognitive processing over generic enterprise utility. |
| "Copilot-first narrative" | **Azure AI Search Grounded Reasoning** | Shifts the focus from conversational UX to robust, verifiable backend retrieval and logic. |
| "Chat with your policies" | **Explainable Decision Making** | Removes chatbot framing; emphasizes the auditability of the reasoning trace. |

## Architectural Integrity

We have ensured that no false claims are made about the architecture. The system relies entirely on:
1. **Azure AI Search** (Hybrid Retrieval + Semantic Ranking) for all knowledge grounding.
2. A customized **ProviderChain** for multi-step logical deduction.

By stripping away the "Copilot" dependency claims, the application's true innovation—detecting semantic impossibilities between conflicting corporate mandates without human prompting—is brought to the forefront.
