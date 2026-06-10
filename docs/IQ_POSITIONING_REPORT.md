# IQ Tool Positioning Review

**Date:** 2026-06-11
**Objective:** Rectify the conflation of "Foundry IQ" and "Azure AI Search" to prevent judges from assuming the project is exaggerating its Microsoft integrations.

## Problem Statement
The current documentation and codebase heavily use the term "Foundry IQ" to describe the retrieval and grounding process. However, the actual technical implementation relies on **Azure AI Search** (specifically Hybrid Retrieval and Semantic Ranking). Misrepresenting standard Azure AI Search as "Foundry IQ" is a critical risk when presenting to Microsoft AI Architects and Foundry Engineers.

## Required Language Shifts

We must transition from marketing exaggeration to technical accuracy. 

### 1. General Grounding and Retrieval
- **Current:** "Grounded entirely in Foundry IQ..."
- **Replacement:** "Grounded entirely via Azure AI Search (Hybrid + Semantic Retrieval)..."
- **Why:** Accurately describes the vector/keyword + semantic reranking pipeline actually built.

### 2. Architecture and Data Flow
- **Current:** "`DocumentAnalyzer` retrieves grounded evidence from Azure Foundry IQ..."
- **Replacement:** "`DocumentAnalyzer` retrieves highly correlated, grounded evidence using Azure AI Search..."
- **Why:** Maintains the emphasis on grounding and evidence without claiming an SDK/service that isn't present.

### 3. Trust and Hallucination Prevention
- **Current:** "Foundry IQ is not just a backend dependency. It is the mechanism that makes the product trustworthy..."
- **Replacement:** "Azure AI Search's Semantic Ranker is the mechanism that makes the product trustworthy by ensuring only high-relevance, factual chunks reach the LLM..."
- **Why:** Demonstrates deep understanding of *why* Azure AI Search prevents hallucinations, which is a stronger architectural argument.

### 4. Code and Prompt References
- **Current:** "You receive N policy statements... each from a different authoritative source document with a Foundry IQ citation." (e.g., in `prompts/conflict_detector.txt`)
- **Replacement:** "...with an Azure AI Search citation."
- **Why:** Aligns the agent prompts with the actual infrastructure.

### 5. UI Elements
- **Current:** "Azure Foundry IQ Grounding & Evidence" or "Powered by Azure Foundry IQ."
- **Replacement:** "Azure AI Search Grounding & Evidence" or "Powered by Azure AI Search."
- **Why:** Ensures the visual demo matches the technical reality.

## Execution Plan
We will perform targeted updates across `README.md`, `submission_assets/*`, and key UI components/prompts to implement these language shifts. This is a low-risk documentation and copy change that significantly improves architectural credibility.
