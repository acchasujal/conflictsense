# Ablation Study: The Architectural Necessity of Azure AI Search

To prove that ConflictSense is not merely a generic RAG wrapper around an LLM, we conducted an ablation study removing **Azure AI Search** from the pipeline and relying solely on standard vector search or raw LLM context windows.

## Scenario: The Whistleblower vs. Security Logging Conflict

**The Challenge:** Identify the contradiction between the Whistleblower anonymity guarantee (Document A) and the Universal security logging mandate (Document B).

### Test 1: WITHOUT Azure AI Search (Standard Vector Search)
* **Setup:** Documents embedded using a standard open-source embedding model; retrieval via basic cosine similarity.
* **Result:** **FAILED**. 
* **Observation:** Standard vector search failed to retrieve the Universal security logging mandate when queried about the Whistleblower policy because the lexical overlap was too low. The LLM analyzed only the Whistleblower document and confidently asserted no conflicts existed.
* **Impact:** Reduced grounding, missing citations, and zero ability to perform large-document comparison across disjointed terminologies.

### Test 2: WITH Azure AI Search (Hybrid Retrieval + Semantic Ranking)
* **Setup:** Current architecture.
* **Result:** **SUCCESS**.
* **Observation:** Azure AI Search's Semantic Ranking correctly identified the logical relationship between "anonymity" and "IP logging," despite the lack of keyword matching. It surfaced both passages to the `DocumentAnalyzer`.
* **Impact:**
  * **Grounded Retrieval:** The `ProviderChain` received exactly the two conflicting paragraphs.
  * **Source Attribution:** The UI correctly cited both documents with >90% confidence.
  * **Explainable Evidence:** The Reasoning Trace clearly articulated *why* logging an IP address violates the anonymity guarantee.

## Conclusion

Azure AI Search is architecturally necessary for ConflictSense. The reasoning agents are completely blind to structural enterprise conflicts without the semantic ranking capabilities provided by Azure.
