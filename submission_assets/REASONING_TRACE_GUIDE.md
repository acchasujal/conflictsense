# Reasoning Trace Visibility Guide

## Why the Reasoning Trace is the Hero

In traditional enterprise search and generic RAG applications, the reasoning that leads to an AI's output is often hidden in backend logs or obscured by conversational UI. This creates a critical trust deficit—especially in legal, HR, and compliance domains where every decision must be auditable.

ConflictSense flips this paradigm. 

The **Reasoning Trace** is not a supporting panel; it consumes nearly 50% of the analysis UI. By making the trace the primary visual element, we guarantee that the user is not just given an answer, but is guided step-by-step through the AI's internal logic.

## How Conclusions Are Formed

Unlike debugging terminals that dump raw JSON or timestamped function calls, the ConflictSense reasoning trace is designed for human legibility. 

1. **Prose Over Logs**: Conclusions are rendered as readable prose paragraphs, ensuring business stakeholders can follow the logic without parsing code syntax.
2. **Intermediate Steps Visible**: The trace reveals intermediate steps (e.g., retrieving DPDP directives, scanning for IT security overlaps) in real time.
3. **Citations First**: Every DocumentAnalyzer step explicitly cites the source document and section, directly attributing the data to Azure AI Search's (Foundry IQ) retrieval engine.

## How Confidence is Determined

Every finding is assigned a Confidence Score, visibly rendered in the trace:

- **90–100% (Critical)**: Unambiguous contradiction with explicit policy overlap.
- **75–89% (High Confidence)**: Strong likelihood of conflict based on semantic similarity of obligations.
- **60–74% (Needs Human Review)**: Potential edge-case or context-dependent conflict.
- **Below 60% (Informational)**: Kept off the primary dashboard but retained in the trace for full auditability.

*This radical transparency is what differentiates a "Reasoning Agent" from a "Chatbot".*
