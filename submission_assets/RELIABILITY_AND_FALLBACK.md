# Reliability and Fallback Systems

Enterprise applications must handle outages gracefully. ConflictSense implements a robust, three-tier fallback architecture to guarantee that reasoning traces and conflict detection remain available, even during catastrophic cloud provider outages.

## The Fallback Chain

### Tier 1: Azure AI Search + Primary Provider (Optimal)
This is the standard execution path. The system queries the Knowledge Base via **Azure AI Search (Hybrid Retrieval + Semantic Ranking)**. The primary LLM provider (via ProviderChain) processes the retrieved context. This tier provides the highest confidence scores and the most accurate citations.

### Tier 2: Provider Fallback (Degraded Reasoning)
*Triggered when:* The primary LLM provider times out or returns a 5xx error.
*Action:* The ProviderChain automatically routes the Azure AI Search context to a secondary, pre-configured LLM provider.
*Impact:* Retrieval remains grounded and accurate (thanks to Azure), but the nuance of the reasoning trace may slightly degrade depending on the secondary model's capabilities. 

### Tier 3: Mock Fallback (Client-Side Simulation)
*Triggered when:* The backend Server-Sent Events (SSE) stream fails entirely (e.g., the FastAPI server is down, or Azure AI Search is completely unreachable).
*Action:* The React frontend automatically detects the `onError` event from the stream and immediately pivots to local execution.
*Implementation Evidence:*
```javascript
// frontend/src/App.jsx
const runLocalFallback = useCallback(() => {
  console.warn('[App] Backend unavailable — activating Tier 3 client-side mock mode');
  setIsMockMode(true);
  // ... local timer-based simulation using MOCK_TRACE_STEPS
});
```
*Impact:* The UI displays a warning banner: `⚠ [MOCK MODE] — Live API unavailable. Displaying pre-computed responses.` The demo can proceed flawlessly using statically cached reasoning traces, ensuring presentation continuity during judging or critical stakeholder reviews.

## Why This Matters

This architecture ensures zero downtime for the user experience while maintaining absolute transparency about the system's operational state. Fake behavior is never passed off as live analysis.
