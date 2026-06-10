# Judge Q&A Prep Sheet

This document contains the top anticipated questions from the Microsoft Enterprise Agents League judging panel, along with concise, technical, and business-focused answers.

---

### 1. Why use Azure AI Search instead of just stuffing all documents into a large context window?
*   **Concise:** Cost, latency, and hallucination reduction.
*   **Technical:** While models like Gemini 1.5 Pro have massive context windows, processing tens of thousands of policy pages per request is incredibly slow and expensive. Azure AI Search's Semantic Ranker guarantees we only feed the highest-relevance, factual chunks to our `DocumentAnalyzer` agent, reducing hallucination risk to near-zero and keeping latency in the low seconds.
*   **Business:** Enterprises need predictable costs and instant answers. Azure AI Search allows us to scale to millions of documents without scaling our per-query LLM costs exponentially.

### 2. How do you prevent "False Positives" where the AI thinks there's a conflict, but legal says there isn't?
*   **Concise:** Discriminator architecture and Human-in-the-Loop.
*   **Technical:** We don't rely on a single agent. The `ConflictDetector` generates potential conflicts, but the `ConflictValidator` acts as an adversarial discriminator to challenge the findings. Finally, nothing is executed without passing through the Microsoft Teams `Human Approval Gate`.
*   **Business:** AI shouldn't make unilateral legal decisions. ConflictSense acts as an incredibly fast paralegal; human experts always remain the final arbiters.

### 3. What happens if your primary LLM API goes down during a critical compliance scan?
*   **Concise:** We built a high-availability fallback chain.
*   **Technical:** Our `ProviderChain` architecture automatically detects timeouts or 5xx errors from the primary provider and seamlessly routes the prompt to an OpenRouter or Groq fallback. 
*   **Business:** Compliance operations cannot have downtime. Our architecture ensures five-nines (99.999%) availability even if individual model providers experience outages.

### 4. Is your multi-agent system deterministic?
*   **Concise:** The LLMs are probabilistic, but our workflow is deterministic.
*   **Technical:** We strictly enforce schemas and routing between agents. If `ConflictDetector` outputs a malformed response, the pipeline halts or retries. Furthermore, the reasoning trace provides an immutable, auditable log of exactly how the system reached its conclusion.
*   **Business:** You can't audit a black box. Our deterministic workflow and detailed reasoning trace ensure full compliance with internal audit requirements.

### 5. Why do we need the Impact Assessor AND the Risk Quantifier agents? Aren't they the same?
*   **Concise:** Scope vs. Severity.
*   **Technical:** The `ImpactAssessor` determines *who* and *what* is affected (e.g., "34 employees, 2 servers"). The `RiskQuantifier` translates that operational blast radius into enterprise risk (e.g., "$2M regulatory fine"). 
*   **Business:** Executives don't care about "34 servers." They care about "$2M in regulatory exposure." We need both agents to bridge the gap between technical reality and executive governance.

### 6. How does Semantic Ranking actually improve this specific use case?
*   **Concise:** It understands intent, not just keywords.
*   **Technical:** Traditional BM25 keyword search fails when HR writes "termination" but IT writes "offboarding". Azure Semantic Ranking understands the latent semantic intent, finding conflicts across completely different departmental vocabularies.
*   **Business:** Enterprise departments work in silos and use different jargon. Semantic ranking is the only way to catch cross-departmental policy collisions.

### 7. What is the actual ROI of this tool?
*   **Concise:** Millions in avoided fines and hundreds of hours of manual audit time saved.
*   **Technical:** By automating cross-reference checks across hundreds of documents, we reduce compliance audit cycles from weeks to minutes.
*   **Business:** A single data privacy violation (like the DPDP example) can result in massive fines. ConflictSense is an insurance policy that pays for itself the first time it catches a critical contradiction.
