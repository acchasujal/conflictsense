# ConflictSense Architecture

This document describes the flow of data through the ConflictSense system, leveraging Microsoft Azure services for high-reliability enterprise policy conflict detection.

## Multi-Agent Architecture powered by Azure AI Search

```mermaid
flowchart TD
    %% Define Styles
    classDef azure fill:#0078D4,color:#fff,stroke:#005A9E,stroke-width:2px;
    classDef agent fill:#111111,color:#fff,stroke:#378ADD,stroke-width:2px;
    classDef human fill:#E81123,color:#fff,stroke:#A80000,stroke-width:2px;
    classDef fallback fill:#505050,color:#fff,stroke:#333333,stroke-width:2px;

    %% Data Sources
    subgraph Data Layer
        KB[Enterprise Knowledge Base \n Policies & Governance] --> Index[Azure AI Search Index]
    end

    %% Retrieval Layer
    subgraph Retrieval Layer
        Index -->|Hybrid Retrieval + Semantic Ranking| Retriever[AzureSearchRetriever]
        class Index,Retriever azure
    end

    %% Ingestion
    Retriever --> DocAnalyzer[DocumentAnalyzer Agent]
    class DocAnalyzer agent
    DocAnalyzer --> ChunkEx[ChunkExtractor]

    %% Provider Fallback
    subgraph ProviderChain [Provider Chain \n High-Availability Routing]
        ChunkEx --> Primary[Primary LLM]
        Primary -.->|Timeout / Failure| OpenRouter[OpenRouter Fallback]
        OpenRouter -.->|Failure| Groq[Groq Fallback]
        class Primary,OpenRouter,Groq fallback
    end

    %% Agent Swarm
    subgraph Agentic Pipeline [Agentic Conflict Detection Pipeline]
        Primary --> CD[ConflictDetector Agent]
        CD --> CV[ConflictValidator Agent]
        CV --> IA[ImpactAssessor Agent]
        IA --> RQ[RiskQuantifier Agent]
        RQ --> RR[ResolutionRecommender Agent]
        class CD,CV,IA,RQ,RR agent
    end

    %% Action Layer
    subgraph Human-in-the-loop
        RR --> Teams[Microsoft Teams \n Approval Gate]
        Teams -->|Approve| Action[Execute Remediation]
        Teams -->|Reject| FalsePos[Log False Positive]
        Teams -->|Assign| Legal[Route to Legal]
        class Teams human
    end
```

## Why Azure AI Search?

ConflictSense relies on **Azure AI Search** to ensure enterprise-grade reliability and avoid LLM hallucination:

1. **Hybrid Retrieval**: Combines traditional BM25 keyword matching with vector similarity search, ensuring we find both exact legal terms (e.g., "DPDP") and semantic intents (e.g., "employee privacy").
2. **Semantic Ranking**: We utilize Azure's state-of-the-art semantic ranker (powered by Microsoft's Turing models) to rerank the top results, ensuring only the most contextually relevant chunks are fed into the LLM context window. This minimizes noise and reduces token costs.
3. **Data Residency & Security**: By keeping enterprise documents indexed within Azure, we maintain strict compliance with data governance policies, a critical requirement for enterprise deployment.
